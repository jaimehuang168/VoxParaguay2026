"""
VoxParaguay 2026 - Real-time Sentiment Service
Manages department-level sentiment averages in Redis with WebSocket broadcast

Features:
- Running average calculation per department
- Real-time WebSocket notifications
- Sentiment history tracking
"""

import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List, Set
import redis.asyncio as redis
from fastapi import WebSocket

from app.core.config import settings


# ============ PARAGUAY DEPARTMENTS ============

PARAGUAY_DEPARTMENTS = [
    "PY-ASU", "PY-1", "PY-2", "PY-3", "PY-4", "PY-5", "PY-6", "PY-7",
    "PY-8", "PY-9", "PY-10", "PY-11", "PY-12", "PY-13", "PY-14",
    "PY-15", "PY-16", "PY-19"
]


class SentimentService:
    """
    Real-time sentiment tracking service using Redis.

    Redis Key Structure:
    - sentiment:dept:{dept_id}:sum    - Running sum of sentiment scores
    - sentiment:dept:{dept_id}:count  - Number of responses
    - sentiment:current               - Hash of current averages per dept
    - sentiment:history:{dept_id}     - List of recent scores (for trends)
    """

    PREFIX_SUM = "sentiment:dept:{}:sum"
    PREFIX_COUNT = "sentiment:dept:{}:count"
    KEY_CURRENT = "sentiment:current"
    PREFIX_HISTORY = "sentiment:history:{}"
    CHANNEL_UPDATES = "sentiment:updates"

    # Maximum history items per department
    MAX_HISTORY = 100

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._websocket_clients: Set[WebSocket] = set()
        self._broadcast_lock = asyncio.Lock()

    async def get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    # ============ CORE SENTIMENT OPERATIONS ============

    async def record_sentiment(
        self,
        department_id: str,
        sentiment_score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record a new sentiment score and update the running average.

        Args:
            department_id: ISO 3166-2:PY code (e.g., "PY-ASU")
            sentiment_score: Score between -1.0 and 1.0
            metadata: Optional additional data (topic, channel, etc.)

        Returns:
            Updated department sentiment info
        """
        if department_id not in PARAGUAY_DEPARTMENTS:
            raise ValueError(f"Invalid department ID: {department_id}")

        if not -1.0 <= sentiment_score <= 1.0:
            raise ValueError(f"Sentiment score must be between -1 and 1: {sentiment_score}")

        r = await self.get_redis()
        now = datetime.now().isoformat()

        # Use pipeline for atomic operations
        async with r.pipeline() as pipe:
            # Increment sum and count
            sum_key = self.PREFIX_SUM.format(department_id)
            count_key = self.PREFIX_COUNT.format(department_id)

            await pipe.incrbyfloat(sum_key, sentiment_score)
            await pipe.incr(count_key)

            # Execute pipeline
            results = await pipe.execute()

        new_sum = results[0]
        new_count = results[1]

        # Calculate new average
        new_average = new_sum / new_count if new_count > 0 else 0.0
        new_average = round(new_average, 4)

        # Update current average hash
        await r.hset(self.KEY_CURRENT, department_id, new_average)

        # Add to history (with limit)
        history_key = self.PREFIX_HISTORY.format(department_id)
        history_entry = json.dumps({
            "score": sentiment_score,
            "timestamp": now,
            "metadata": metadata,
        })
        await r.lpush(history_key, history_entry)
        await r.ltrim(history_key, 0, self.MAX_HISTORY - 1)

        # Prepare update payload
        update_data = {
            "type": "sentiment_update",
            "department_id": department_id,
            "sentiment_score": sentiment_score,
            "average": new_average,
            "total_count": new_count,
            "timestamp": now,
            "metadata": metadata,
        }

        # Publish to Redis channel (for multiple backend instances)
        await r.publish(self.CHANNEL_UPDATES, json.dumps(update_data))

        # Broadcast to connected WebSocket clients
        await self.broadcast_update(update_data)

        return update_data

    async def get_department_sentiment(self, department_id: str) -> Dict[str, Any]:
        """Get current sentiment data for a department."""
        r = await self.get_redis()

        sum_key = self.PREFIX_SUM.format(department_id)
        count_key = self.PREFIX_COUNT.format(department_id)

        total_sum = float(await r.get(sum_key) or 0)
        count = int(await r.get(count_key) or 0)

        average = total_sum / count if count > 0 else None

        return {
            "department_id": department_id,
            "average": round(average, 4) if average is not None else None,
            "total_count": count,
        }

    async def get_all_sentiments(self) -> Dict[str, float]:
        """
        Get current sentiment averages for all departments.

        Returns:
            Dict mapping department IDs to sentiment averages
        """
        r = await self.get_redis()

        # Get all current averages
        result = await r.hgetall(self.KEY_CURRENT)

        # Convert to float values
        sentiments = {}
        for dept_id, value in result.items():
            try:
                sentiments[dept_id] = float(value)
            except (ValueError, TypeError):
                sentiments[dept_id] = 0.0

        return sentiments

    async def get_department_history(
        self,
        department_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get recent sentiment history for a department."""
        r = await self.get_redis()
        history_key = self.PREFIX_HISTORY.format(department_id)

        raw_items = await r.lrange(history_key, 0, limit - 1)

        history = []
        for item in raw_items:
            try:
                history.append(json.loads(item))
            except json.JSONDecodeError:
                pass

        return history

    # ============ WEBSOCKET MANAGEMENT ============

    async def register_websocket(self, websocket: WebSocket) -> None:
        """Register a WebSocket client for real-time updates."""
        async with self._broadcast_lock:
            self._websocket_clients.add(websocket)

    async def unregister_websocket(self, websocket: WebSocket) -> None:
        """Unregister a WebSocket client."""
        async with self._broadcast_lock:
            self._websocket_clients.discard(websocket)

    async def broadcast_update(self, data: Dict[str, Any]) -> None:
        """Broadcast sentiment update to all connected WebSocket clients."""
        if not self._websocket_clients:
            return

        message = json.dumps(data)
        disconnected = []

        async with self._broadcast_lock:
            for ws in self._websocket_clients:
                try:
                    await ws.send_text(message)
                except Exception:
                    disconnected.append(ws)

            # Clean up disconnected clients
            for ws in disconnected:
                self._websocket_clients.discard(ws)

    async def get_connected_clients_count(self) -> int:
        """Get number of connected WebSocket clients."""
        return len(self._websocket_clients)

    # ============ ADMIN OPERATIONS ============

    async def reset_department(self, department_id: str) -> bool:
        """Reset sentiment data for a department."""
        r = await self.get_redis()

        sum_key = self.PREFIX_SUM.format(department_id)
        count_key = self.PREFIX_COUNT.format(department_id)
        history_key = self.PREFIX_HISTORY.format(department_id)

        await r.delete(sum_key, count_key, history_key)
        await r.hdel(self.KEY_CURRENT, department_id)

        return True

    async def reset_all(self) -> bool:
        """Reset all sentiment data."""
        r = await self.get_redis()

        # Delete all department-specific keys
        for dept_id in PARAGUAY_DEPARTMENTS:
            sum_key = self.PREFIX_SUM.format(dept_id)
            count_key = self.PREFIX_COUNT.format(dept_id)
            history_key = self.PREFIX_HISTORY.format(dept_id)
            await r.delete(sum_key, count_key, history_key)

        # Delete current averages hash
        await r.delete(self.KEY_CURRENT)

        return True

    async def get_stats(self) -> Dict[str, Any]:
        """Get overall sentiment statistics."""
        r = await self.get_redis()

        total_responses = 0
        departments_with_data = 0

        for dept_id in PARAGUAY_DEPARTMENTS:
            count_key = self.PREFIX_COUNT.format(dept_id)
            count = int(await r.get(count_key) or 0)
            total_responses += count
            if count > 0:
                departments_with_data += 1

        return {
            "total_responses": total_responses,
            "departments_total": len(PARAGUAY_DEPARTMENTS),
            "departments_with_data": departments_with_data,
            "connected_clients": await self.get_connected_clients_count(),
        }

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


# ============ SINGLETON ============

_sentiment_service: Optional[SentimentService] = None


def get_sentiment_service() -> SentimentService:
    """Get or create the singleton SentimentService instance."""
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = SentimentService()
    return _sentiment_service
