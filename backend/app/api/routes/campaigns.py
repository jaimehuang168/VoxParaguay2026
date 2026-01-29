"""
VoxParaguay 2026 - Campaign Management Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

router = APIRouter()


class CampaignStatus(str, Enum):
    DRAFT = "borrador"
    ACTIVE = "activo"
    PAUSED = "pausado"
    COMPLETED = "completado"


class CampaignCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    fecha_inicio: datetime
    fecha_fin: datetime
    regiones: list[str] = ["Asunción", "Central", "Alto Paraná", "Itapúa"]
    meta_encuestas: int = 1000


class CampaignResponse(BaseModel):
    id: str
    nombre: str
    descripcion: Optional[str]
    estado: CampaignStatus
    fecha_inicio: datetime
    fecha_fin: datetime
    regiones: list[str]
    meta_encuestas: int
    encuestas_completadas: int
    created_at: datetime


class SurveyQuestion(BaseModel):
    id: str
    orden: int
    texto: str
    tipo: str  # "escala", "opcion_multiple", "texto_libre"
    opciones: Optional[list[str]] = None
    peso: float = 1.0  # Weight for sentiment calculation
    condicion: Optional[dict] = None  # Conditional branching


class SurveyScript(BaseModel):
    campaign_id: str
    preguntas: list[SurveyQuestion]


@router.get("/")
async def list_campaigns():
    """Listar todas las campañas."""
    # TODO: Implement with Prisma
    return {"campaigns": [], "total": 0}


@router.post("/")
async def create_campaign(campaign: CampaignCreate):
    """Crear nueva campaña de encuestas."""
    # TODO: Implement with Prisma
    return {"message": "Campaña creada exitosamente", "id": "temp-id"}


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: str):
    """Obtener detalles de una campaña específica."""
    # TODO: Implement with Prisma
    raise HTTPException(status_code=404, detail="Campaña no encontrada")


@router.put("/{campaign_id}")
async def update_campaign(campaign_id: str, campaign: CampaignCreate):
    """Actualizar campaña existente."""
    # TODO: Implement with Prisma
    return {"message": "Campaña actualizada exitosamente"}


@router.post("/{campaign_id}/script")
async def set_survey_script(campaign_id: str, script: SurveyScript):
    """Configurar el guión de preguntas para la campaña."""
    # TODO: Implement with Prisma
    return {"message": "Guión configurado exitosamente"}


@router.get("/{campaign_id}/script")
async def get_survey_script(campaign_id: str):
    """Obtener el guión de preguntas de la campaña."""
    # TODO: Implement with Prisma
    return {"preguntas": []}


@router.post("/{campaign_id}/activate")
async def activate_campaign(campaign_id: str):
    """Activar una campaña."""
    # TODO: Implement with Prisma
    return {"message": "Campaña activada", "estado": CampaignStatus.ACTIVE}


@router.post("/{campaign_id}/pause")
async def pause_campaign(campaign_id: str):
    """Pausar una campaña activa."""
    # TODO: Implement with Prisma
    return {"message": "Campaña pausada", "estado": CampaignStatus.PAUSED}
