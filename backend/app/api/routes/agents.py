"""
VoxParaguay 2026 - Agent Management Routes
Real-time scheduling with Redis Least Connections algorithm
"""

import json
import asyncio
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

from app.utils.redis_agent_manager import (
    get_agent_manager,
    RedisAgentManager,
    AgentStatus as RedisAgentStatus
)

router = APIRouter()


class AgentStatus(str, Enum):
    AVAILABLE = "disponible"
    BUSY = "ocupado"
    OFFLINE = "desconectado"
    BREAK = "descanso"


class AgentCreate(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None
    region: Optional[str] = None
    skills: Optional[List[str]] = None


class AgentLoginRequest(BaseModel):
    agent_id: str
    nombre: str
    region: Optional[str] = None
    skills: Optional[List[str]] = None


class AgentResponse(BaseModel):
    id: str
    nombre: str
    email: str
    estado: AgentStatus
    encuestas_completadas_hoy: int
    tiempo_promedio_encuesta: float
    created_at: datetime


class ConversationAssignRequest(BaseModel):
    conversation_id: str
    channel: str  # voice, whatsapp, facebook, instagram
    region: Optional[str] = None
    required_skills: Optional[List[str]] = None


# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self._redis_listener_task: Optional[asyncio.Task] = None
        self._running = False

    async def connect(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[agent_id] = websocket

        # Start Redis pub/sub listener if not running
        if not self._running:
            self._running = True
            self._redis_listener_task = asyncio.create_task(
                self._listen_redis_events()
            )

    def disconnect(self, agent_id: str):
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]

        # Stop listener if no connections
        if not self.active_connections and self._redis_listener_task:
            self._running = False
            self._redis_listener_task.cancel()
            self._redis_listener_task = None

    async def send_to_agent(self, agent_id: str, message: dict):
        if agent_id in self.active_connections:
            try:
                await self.active_connections[agent_id].send_json(message)
            except Exception:
                self.disconnect(agent_id)

    async def broadcast(self, message: dict):
        disconnected = []
        for agent_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(agent_id)

        for agent_id in disconnected:
            self.disconnect(agent_id)

    async def _listen_redis_events(self):
        """Listen to Redis pub/sub for agent events and broadcast to WebSockets."""
        try:
            redis_manager = get_agent_manager()
            r = await redis_manager.get_redis()
            pubsub = r.pubsub()
            await pubsub.subscribe("agent:events")

            while self._running:
                try:
                    message = await asyncio.wait_for(
                        pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=1.0
                    )
                    if message and message["type"] == "message":
                        event_data = json.loads(message["data"])
                        await self.broadcast({
                            "type": "agent_event",
                            "event": event_data
                        })
                except asyncio.TimeoutError:
                    continue
                except Exception:
                    await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        except Exception:
            pass


manager = ConnectionManager()


def get_redis_manager() -> RedisAgentManager:
    return get_agent_manager()


# ============ REST ENDPOINTS ============

@router.get("/")
async def list_agents(redis_mgr: RedisAgentManager = Depends(get_redis_manager)):
    """Listar todos los agentes en línea."""
    agents = await redis_mgr.get_all_agents_status()
    return {
        "agents": agents,
        "total": len(agents),
        "mensaje": "Lista de agentes activos"
    }


@router.post("/")
async def create_agent(agent: AgentCreate):
    """Crear nuevo agente (persistencia en base de datos)."""
    # TODO: Implement with Prisma for permanent storage
    return {"message": "Agente creado exitosamente", "id": "temp-id"}


@router.post("/login")
async def agent_login(
    request: AgentLoginRequest,
    redis_mgr: RedisAgentManager = Depends(get_redis_manager)
):
    """
    Registrar agente como en línea y disponible.
    Actualiza Redis para el algoritmo de Least Connections.
    """
    agent_data = await redis_mgr.agent_login(
        agent_id=request.agent_id,
        agent_name=request.nombre,
        region=request.region,
        skills=request.skills
    )

    return {
        "mensaje": "Agente conectado exitosamente",
        "agente": agent_data
    }


@router.post("/logout/{agent_id}")
async def agent_logout(
    agent_id: str,
    redis_mgr: RedisAgentManager = Depends(get_redis_manager)
):
    """Desconectar agente del sistema."""
    success = await redis_mgr.agent_logout(agent_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Agente no encontrado o ya desconectado"
        )

    return {"mensaje": "Agente desconectado exitosamente"}


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    redis_mgr: RedisAgentManager = Depends(get_redis_manager)
):
    """Obtener estado actual del agente."""
    agent_data = await redis_mgr.get_agent_status(agent_id)

    if not agent_data:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    return agent_data


@router.put("/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status: AgentStatus,
    redis_mgr: RedisAgentManager = Depends(get_redis_manager)
):
    """Actualizar estado del agente (disponible, ocupado, descanso)."""
    redis_status = RedisAgentStatus(status.value)
    success = await redis_mgr.update_agent_status(agent_id, redis_status)

    if not success:
        raise HTTPException(status_code=404, detail="Agente no encontrado")

    return {
        "mensaje": "Estado actualizado",
        "estado": status.value
    }


@router.get("/{agent_id}/conversations")
async def get_agent_conversations(agent_id: str):
    """Obtener conversaciones activas del agente."""
    # TODO: Implement with Prisma/Redis
    return {"conversations": []}


# ============ CONVERSATION ASSIGNMENT (LEAST CONNECTIONS) ============

@router.post("/conversations/assign")
async def assign_conversation(
    request: ConversationAssignRequest,
    redis_mgr: RedisAgentManager = Depends(get_redis_manager)
):
    """
    Asignar conversación usando algoritmo Least Connections.
    Selecciona el agente con menor carga actual.
    """
    assigned_agent = await redis_mgr.assign_conversation(
        conversation_id=request.conversation_id,
        channel=request.channel,
        region=request.region,
        required_skills=request.required_skills
    )

    if not assigned_agent:
        raise HTTPException(
            status_code=503,
            detail="No hay agentes disponibles en este momento"
        )

    # Notify assigned agent via WebSocket
    await manager.send_to_agent(assigned_agent["id"], {
        "type": "nueva_conversacion",
        "conversation_id": request.conversation_id,
        "channel": request.channel,
        "timestamp": datetime.now().isoformat()
    })

    return {
        "mensaje": "Conversación asignada exitosamente",
        "agente_asignado": assigned_agent,
        "conversation_id": request.conversation_id
    }


@router.post("/conversations/{conversation_id}/release")
async def release_conversation(
    conversation_id: str,
    agent_id: str,
    redis_mgr: RedisAgentManager = Depends(get_redis_manager)
):
    """Liberar conversación y decrementar carga del agente."""
    success = await redis_mgr.release_conversation(conversation_id, agent_id)

    return {
        "mensaje": "Conversación liberada",
        "conversation_id": conversation_id
    }


# ============ LOAD BALANCING STATS ============

@router.get("/stats/load")
async def get_load_distribution(
    redis_mgr: RedisAgentManager = Depends(get_redis_manager)
):
    """Obtener distribución de carga entre agentes."""
    distribution = await redis_mgr.get_load_distribution()
    return {
        "distribucion_carga": distribution,
        "total_agentes": len(distribution)
    }


@router.get("/stats/regions")
async def get_region_stats(
    redis_mgr: RedisAgentManager = Depends(get_redis_manager)
):
    """Obtener estadísticas por región de Paraguay."""
    stats = await redis_mgr.get_region_stats()
    return {
        "estadisticas_regionales": stats
    }


# ============ WEBSOCKET ENDPOINT ============

@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    agent_id: str,
    agent_name: str = "Agente",
    region: Optional[str] = None
):
    """
    WebSocket para comunicación en tiempo real con agentes.

    Al conectarse:
    - Registra agente en Redis (login automático)
    - Suscribe a eventos de pub/sub

    Maneja:
    - Mensajes entrantes/salientes
    - Respuestas de encuestas
    - Cambios de estado
    - Asignación de conversaciones
    """
    redis_mgr = get_agent_manager()

    # Connect WebSocket
    await manager.connect(agent_id, websocket)

    # Auto-login to Redis
    await redis_mgr.agent_login(
        agent_id=agent_id,
        agent_name=agent_name,
        region=region,
        skills=["voice", "whatsapp"]
    )

    # Notify all agents of new login
    await manager.broadcast({
        "type": "agente_conectado",
        "agent_id": agent_id,
        "agent_name": agent_name,
        "timestamp": datetime.now().isoformat()
    })

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "mensaje_enviado":
                # Agent sent a message to respondent
                await manager.broadcast({
                    "type": "actividad_agente",
                    "agent_id": agent_id,
                    "action": "mensaje_enviado",
                    "timestamp": datetime.now().isoformat()
                })

            elif msg_type == "respuesta_encuesta":
                # Agent recorded a survey response
                await manager.broadcast({
                    "type": "actividad_agente",
                    "agent_id": agent_id,
                    "action": "respuesta_registrada",
                    "timestamp": datetime.now().isoformat()
                })

            elif msg_type == "cambio_estado":
                # Agent changed their status
                new_status = data.get("estado", "disponible")
                await redis_mgr.update_agent_status(
                    agent_id,
                    RedisAgentStatus(new_status)
                )
                await manager.broadcast({
                    "type": "estado_actualizado",
                    "agent_id": agent_id,
                    "estado": new_status,
                    "timestamp": datetime.now().isoformat()
                })

            elif msg_type == "chat_iniciado":
                # Chat/call started - agent becomes busy
                conversation_id = data.get("conversation_id")
                await redis_mgr.update_agent_status(
                    agent_id,
                    RedisAgentStatus.BUSY
                )
                await manager.broadcast({
                    "type": "chat_iniciado",
                    "agent_id": agent_id,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                })

            elif msg_type == "chat_finalizado":
                # Chat/call ended - release and set available
                conversation_id = data.get("conversation_id")
                await redis_mgr.release_conversation(conversation_id, agent_id)
                await redis_mgr.update_agent_status(
                    agent_id,
                    RedisAgentStatus.AVAILABLE
                )
                await manager.broadcast({
                    "type": "chat_finalizado",
                    "agent_id": agent_id,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                })

            elif msg_type == "heartbeat":
                # Keep-alive ping
                await websocket.send_json({
                    "type": "heartbeat_ack",
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        # Auto-logout from Redis
        await redis_mgr.agent_logout(agent_id)
        manager.disconnect(agent_id)

        # Notify all agents of disconnect
        await manager.broadcast({
            "type": "agente_desconectado",
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        # Handle unexpected errors
        await redis_mgr.agent_logout(agent_id)
        manager.disconnect(agent_id)
