"""
VoxParaguay 2026 - Redis Agent Manager
Real-time agent scheduling with Least Connections algorithm

Features:
- Agent status tracking (disponible, ocupado, descanso, desconectado)
- Least Connections load balancing for call/chat assignment
- Real-time metrics per agent
- Region-based routing support
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import redis.asyncio as redis

from app.core.config import settings


class AgentStatus(str, Enum):
    AVAILABLE = "disponible"
    BUSY = "ocupado"
    BREAK = "descanso"
    OFFLINE = "desconectado"


class RedisAgentManager:
    """
    Manages agent availability and load balancing using Redis.
    Implements Least Connections algorithm for optimal distribution.
    """

    # Redis key prefixes
    PREFIX_AGENT = "agent:"
    PREFIX_AGENT_STATUS = "agent:status:"
    PREFIX_AGENT_LOAD = "agent:load:"
    PREFIX_AGENT_METRICS = "agent:metrics:"
    PREFIX_ONLINE_AGENTS = "agents:online"
    PREFIX_REGION_AGENTS = "agents:region:"

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def get_redis(self) -> redis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            self._redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis

    # ============ AGENT STATUS MANAGEMENT ============

    async def agent_login(
        self,
        agent_id: str,
        agent_name: str,
        region: Optional[str] = None,
        skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Register agent as online and available.

        Args:
            agent_id: Unique agent identifier
            agent_name: Agent display name
            region: Primary region (Asunción, Central, etc.)
            skills: List of skills (voice, whatsapp, etc.)

        Returns:
            Agent status info
        """
        r = await self.get_redis()
        now = datetime.now().isoformat()

        agent_data = {
            "id": agent_id,
            "name": agent_name,
            "status": AgentStatus.AVAILABLE,
            "region": region,
            "skills": json.dumps(skills or ["voice", "whatsapp"]),
            "current_connections": 0,
            "login_time": now,
            "last_activity": now,
        }

        # Store agent data
        await r.hset(f"{self.PREFIX_AGENT}{agent_id}", mapping=agent_data)

        # Set status
        await r.set(f"{self.PREFIX_AGENT_STATUS}{agent_id}", AgentStatus.AVAILABLE)

        # Initialize load counter
        await r.set(f"{self.PREFIX_AGENT_LOAD}{agent_id}", 0)

        # Add to online agents set
        await r.sadd(self.PREFIX_ONLINE_AGENTS, agent_id)

        # Add to region set if specified
        if region:
            await r.sadd(f"{self.PREFIX_REGION_AGENTS}{region}", agent_id)

        # Publish login event
        await r.publish("agent:events", json.dumps({
            "type": "login",
            "agent_id": agent_id,
            "agent_name": agent_name,
            "timestamp": now,
        }))

        return agent_data

    async def agent_logout(self, agent_id: str) -> bool:
        """
        Mark agent as offline and remove from available pool.
        """
        r = await self.get_redis()
        now = datetime.now().isoformat()

        # Get agent data for region cleanup
        agent_data = await r.hgetall(f"{self.PREFIX_AGENT}{agent_id}")

        if not agent_data:
            return False

        # Update status
        await r.set(f"{self.PREFIX_AGENT_STATUS}{agent_id}", AgentStatus.OFFLINE)
        await r.hset(f"{self.PREFIX_AGENT}{agent_id}", "status", AgentStatus.OFFLINE)
        await r.hset(f"{self.PREFIX_AGENT}{agent_id}", "logout_time", now)

        # Remove from online set
        await r.srem(self.PREFIX_ONLINE_AGENTS, agent_id)

        # Remove from region set
        region = agent_data.get("region")
        if region:
            await r.srem(f"{self.PREFIX_REGION_AGENTS}{region}", agent_id)

        # Publish logout event
        await r.publish("agent:events", json.dumps({
            "type": "logout",
            "agent_id": agent_id,
            "agent_name": agent_data.get("name"),
            "timestamp": now,
        }))

        return True

    async def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus,
    ) -> bool:
        """Update agent availability status."""
        r = await self.get_redis()
        now = datetime.now().isoformat()

        exists = await r.exists(f"{self.PREFIX_AGENT}{agent_id}")
        if not exists:
            return False

        await r.set(f"{self.PREFIX_AGENT_STATUS}{agent_id}", status)
        await r.hset(f"{self.PREFIX_AGENT}{agent_id}", "status", status)
        await r.hset(f"{self.PREFIX_AGENT}{agent_id}", "last_activity", now)

        # Publish status change
        await r.publish("agent:events", json.dumps({
            "type": "status_change",
            "agent_id": agent_id,
            "status": status,
            "timestamp": now,
        }))

        return True

    # ============ LEAST CONNECTIONS LOAD BALANCING ============

    async def assign_conversation(
        self,
        conversation_id: str,
        channel: str,
        region: Optional[str] = None,
        required_skills: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Assign a conversation to the agent with least connections.

        Algorithm: Least Connections
        1. Get all available agents (optionally filtered by region/skills)
        2. Sort by current connection count (ascending)
        3. Select agent with lowest load
        4. Increment their connection count

        Args:
            conversation_id: Unique conversation ID
            channel: Channel type (voice, whatsapp, etc.)
            region: Preferred region for routing
            required_skills: Required agent skills

        Returns:
            Assigned agent info or None if no agents available
        """
        r = await self.get_redis()

        # Get candidate agents
        if region:
            # Try region-specific agents first
            agent_ids = await r.smembers(f"{self.PREFIX_REGION_AGENTS}{region}")
            if not agent_ids:
                # Fall back to all online agents
                agent_ids = await r.smembers(self.PREFIX_ONLINE_AGENTS)
        else:
            agent_ids = await r.smembers(self.PREFIX_ONLINE_AGENTS)

        if not agent_ids:
            return None

        # Filter by availability and skills, get load counts
        candidates = []

        for agent_id in agent_ids:
            status = await r.get(f"{self.PREFIX_AGENT_STATUS}{agent_id}")

            if status != AgentStatus.AVAILABLE:
                continue

            # Check skills if required
            if required_skills:
                agent_data = await r.hgetall(f"{self.PREFIX_AGENT}{agent_id}")
                agent_skills = json.loads(agent_data.get("skills", "[]"))
                if not all(skill in agent_skills for skill in required_skills):
                    continue

            # Get current load
            load = int(await r.get(f"{self.PREFIX_AGENT_LOAD}{agent_id}") or 0)
            candidates.append((agent_id, load))

        if not candidates:
            return None

        # Sort by load (Least Connections)
        candidates.sort(key=lambda x: x[1])

        # Select agent with least connections
        selected_agent_id = candidates[0][0]

        # Increment connection count
        new_load = await r.incr(f"{self.PREFIX_AGENT_LOAD}{selected_agent_id}")

        # Get full agent data
        agent_data = await r.hgetall(f"{self.PREFIX_AGENT}{selected_agent_id}")
        agent_data["current_connections"] = new_load

        # Update last activity
        now = datetime.now().isoformat()
        await r.hset(f"{self.PREFIX_AGENT}{selected_agent_id}", "last_activity", now)

        # Store conversation assignment
        await r.hset(f"conversation:{conversation_id}", mapping={
            "agent_id": selected_agent_id,
            "channel": channel,
            "assigned_at": now,
            "status": "active",
        })

        # Publish assignment event
        await r.publish("agent:events", json.dumps({
            "type": "conversation_assigned",
            "agent_id": selected_agent_id,
            "conversation_id": conversation_id,
            "channel": channel,
            "timestamp": now,
        }))

        return agent_data

    async def release_conversation(
        self,
        conversation_id: str,
        agent_id: str,
    ) -> bool:
        """
        Release a conversation and decrement agent load.
        """
        r = await self.get_redis()
        now = datetime.now().isoformat()

        # Decrement load (minimum 0)
        current_load = int(await r.get(f"{self.PREFIX_AGENT_LOAD}{agent_id}") or 0)
        if current_load > 0:
            await r.decr(f"{self.PREFIX_AGENT_LOAD}{agent_id}")

        # Update conversation status
        await r.hset(f"conversation:{conversation_id}", "status", "completed")
        await r.hset(f"conversation:{conversation_id}", "completed_at", now)

        # Update agent metrics
        await self._update_agent_metrics(agent_id, "conversations_completed")

        # Publish release event
        await r.publish("agent:events", json.dumps({
            "type": "conversation_released",
            "agent_id": agent_id,
            "conversation_id": conversation_id,
            "timestamp": now,
        }))

        return True

    # ============ METRICS & MONITORING ============

    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current agent status and metrics."""
        r = await self.get_redis()

        agent_data = await r.hgetall(f"{self.PREFIX_AGENT}{agent_id}")
        if not agent_data:
            return None

        load = int(await r.get(f"{self.PREFIX_AGENT_LOAD}{agent_id}") or 0)
        agent_data["current_connections"] = load

        return agent_data

    async def get_all_agents_status(self) -> List[Dict[str, Any]]:
        """Get status of all online agents."""
        r = await self.get_redis()

        agent_ids = await r.smembers(self.PREFIX_ONLINE_AGENTS)
        agents = []

        for agent_id in agent_ids:
            agent_data = await self.get_agent_status(agent_id)
            if agent_data:
                agents.append(agent_data)

        return agents

    async def get_load_distribution(self) -> Dict[str, int]:
        """Get current load distribution across all agents."""
        r = await self.get_redis()

        agent_ids = await r.smembers(self.PREFIX_ONLINE_AGENTS)
        distribution = {}

        for agent_id in agent_ids:
            load = int(await r.get(f"{self.PREFIX_AGENT_LOAD}{agent_id}") or 0)
            agent_data = await r.hgetall(f"{self.PREFIX_AGENT}{agent_id}")
            name = agent_data.get("name", agent_id)
            distribution[name] = load

        return distribution

    async def get_region_stats(self) -> Dict[str, Dict[str, int]]:
        """Get agent counts and load per region."""
        r = await self.get_redis()

        regions = ["Asunción", "Central", "Alto Paraná", "Itapúa"]
        stats = {}

        for region in regions:
            agent_ids = await r.smembers(f"{self.PREFIX_REGION_AGENTS}{region}")
            total_load = 0
            available = 0

            for agent_id in agent_ids:
                status = await r.get(f"{self.PREFIX_AGENT_STATUS}{agent_id}")
                if status == AgentStatus.AVAILABLE:
                    available += 1
                load = int(await r.get(f"{self.PREFIX_AGENT_LOAD}{agent_id}") or 0)
                total_load += load

            stats[region] = {
                "total_agents": len(agent_ids),
                "available": available,
                "total_load": total_load,
            }

        return stats

    async def _update_agent_metrics(self, agent_id: str, metric: str) -> None:
        """Increment an agent metric counter."""
        r = await self.get_redis()
        await r.hincrby(f"{self.PREFIX_AGENT_METRICS}{agent_id}", metric, 1)

    # ============ CLEANUP ============

    async def cleanup_stale_agents(self, timeout_minutes: int = 30) -> int:
        """
        Remove agents who haven't been active for specified time.
        Returns count of cleaned up agents.
        """
        r = await self.get_redis()
        cutoff = datetime.now() - timedelta(minutes=timeout_minutes)
        cleaned = 0

        agent_ids = await r.smembers(self.PREFIX_ONLINE_AGENTS)

        for agent_id in agent_ids:
            agent_data = await r.hgetall(f"{self.PREFIX_AGENT}{agent_id}")
            last_activity = agent_data.get("last_activity")

            if last_activity:
                last_dt = datetime.fromisoformat(last_activity)
                if last_dt < cutoff:
                    await self.agent_logout(agent_id)
                    cleaned += 1

        return cleaned

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


# Singleton instance
_agent_manager: Optional[RedisAgentManager] = None


def get_agent_manager() -> RedisAgentManager:
    """Get or create the singleton RedisAgentManager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = RedisAgentManager()
    return _agent_manager
