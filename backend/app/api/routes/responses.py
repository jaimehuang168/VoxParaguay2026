"""
VoxParaguay 2026 - Survey Response Routes
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime

router = APIRouter()


class ResponseCreate(BaseModel):
    campaign_id: str
    agent_id: str
    respondent_id: str
    question_id: str
    respuesta: Union[str, int, float]
    canal: str  # "voice", "whatsapp", "facebook", "instagram"
    duracion_segundos: Optional[int] = None


class SurveySessionCreate(BaseModel):
    campaign_id: str
    agent_id: str
    canal: str
    telefono_encriptado: str  # Encrypted phone for duplicate detection


class SurveySessionComplete(BaseModel):
    session_id: str
    completado: bool = True
    notas: Optional[str] = None


@router.post("/session/start")
async def start_survey_session(session: SurveySessionCreate):
    """
    Iniciar nueva sesión de encuesta.
    Verifica duplicados usando hash del teléfono encriptado.
    """
    # TODO: Implement duplicate check and session creation
    return {
        "session_id": "temp-session-id",
        "message": "Sesión iniciada exitosamente"
    }


@router.post("/session/complete")
async def complete_survey_session(session: SurveySessionComplete):
    """Completar sesión de encuesta."""
    # TODO: Implement session completion
    return {"message": "Sesión completada exitosamente"}


@router.post("/")
async def record_response(response: ResponseCreate):
    """Registrar respuesta individual de encuesta."""
    # TODO: Implement with Prisma
    return {"message": "Respuesta registrada", "id": "temp-id"}


@router.get("/campaign/{campaign_id}")
async def get_campaign_responses(
    campaign_id: str,
    region: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
):
    """Obtener todas las respuestas de una campaña."""
    # TODO: Implement with Prisma
    return {"responses": [], "total": 0}


@router.get("/session/{session_id}")
async def get_session_responses(session_id: str):
    """Obtener todas las respuestas de una sesión específica."""
    # TODO: Implement with Prisma
    return {"responses": []}


@router.post("/check-duplicate")
async def check_duplicate_respondent(
    campaign_id: str,
    telefono_hash: str,
):
    """
    Verificar si el encuestado ya participó en esta campaña.
    Compara hash del teléfono encriptado para proteger privacidad.
    """
    # TODO: Implement duplicate check
    return {"is_duplicate": False}
