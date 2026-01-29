"""
VoxParaguay 2026 - Redis Queue Service
Handles async message processing from Twilio and Meta webhooks
"""

import json
from typing import Optional
import redis.asyncio as redis
from app.core.config import settings


class QueueService:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    async def push_message(self, message: dict, queue_name: str = "incoming_messages"):
        """Push a message to the Redis queue."""
        r = await self.get_redis()
        await r.rpush(queue_name, json.dumps(message))

    async def pop_message(self, queue_name: str = "incoming_messages", timeout: int = 0) -> Optional[dict]:
        """Pop a message from the Redis queue (blocking)."""
        r = await self.get_redis()
        result = await r.blpop(queue_name, timeout=timeout)
        if result:
            _, message = result
            return json.loads(message)
        return None

    async def get_queue_length(self, queue_name: str = "incoming_messages") -> int:
        """Get the current queue length."""
        r = await self.get_redis()
        return await r.llen(queue_name)

    async def link_message_to_campaign(self, message_id: str, campaign_id: str):
        """Associate a message with a campaign."""
        r = await self.get_redis()
        await r.hset("message_campaigns", message_id, campaign_id)

    async def get_campaign_for_message(self, message_id: str) -> Optional[str]:
        """Get the campaign ID for a message."""
        r = await self.get_redis()
        return await r.hget("message_campaigns", message_id)

    async def cache_conversation(self, conversation_id: str, data: dict, ttl: int = 3600):
        """Cache conversation state for quick access."""
        r = await self.get_redis()
        await r.setex(
            f"conversation:{conversation_id}",
            ttl,
            json.dumps(data)
        )

    async def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """Get cached conversation state."""
        r = await self.get_redis()
        data = await r.get(f"conversation:{conversation_id}")
        if data:
            return json.loads(data)
        return None

    async def publish_event(self, channel: str, event: dict):
        """Publish event for real-time updates."""
        r = await self.get_redis()
        await r.publish(channel, json.dumps(event))

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


queue_service = QueueService()
