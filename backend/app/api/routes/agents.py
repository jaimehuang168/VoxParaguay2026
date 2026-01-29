"""
VoxParaguay 2026 - Agent Management Routes
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

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


class AgentResponse(BaseModel):
    id: str
    nombre: str
    email: str
    estado: AgentStatus
    encuestas_completadas_hoy: int
    tiempo_promedio_encuesta: float  # in minutes
    created_at: datetime


# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, agent_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[agent_id] = websocket

    def disconnect(self, agent_id: str):
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]

    async def send_to_agent(self, agent_id: str, message: dict):
        if agent_id in self.active_connections:
            await self.active_connections[agent_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@router.get("/")
async def list_agents():
    """Listar todos los agentes."""
    # TODO: Implement with Prisma
    return {"agents": [], "total": 0}


@router.post("/")
async def create_agent(agent: AgentCreate):
    """Crear nuevo agente."""
    # TODO: Implement with Prisma
    return {"message": "Agente creado exitosamente", "id": "temp-id"}


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Obtener detalles de un agente."""
    # TODO: Implement with Prisma
    raise HTTPException(status_code=404, detail="Agente no encontrado")


@router.put("/{agent_id}/status")
async def update_agent_status(agent_id: str, status: AgentStatus):
    """Actualizar estado del agente."""
    # TODO: Implement with Prisma
    return {"message": "Estado actualizado", "estado": status}


@router.get("/{agent_id}/conversations")
async def get_agent_conversations(agent_id: str):
    """Obtener conversaciones activas del agente."""
    # TODO: Implement with Prisma
    return {"conversations": []}


@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """
    WebSocket connection for real-time agent communication.
    Handles:
    - New incoming messages/calls
    - Survey script updates
    - Status changes
    """
    await manager.connect(agent_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            # Handle different message types
            if data.get("type") == "message_sent":
                # Agent sent a message to respondent
                pass
            elif data.get("type") == "survey_response":
                # Agent recorded a survey response
                pass
            elif data.get("type") == "status_change":
                # Agent changed their status
                await update_agent_status(agent_id, AgentStatus(data.get("status")))

    except WebSocketDisconnect:
        manager.disconnect(agent_id)
