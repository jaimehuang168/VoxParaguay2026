"""
VoxParaguay 2026 - Survey Response Routes
Includes real-time sentiment ingest endpoint
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Union, Dict, Any
from datetime import datetime

from app.services.sentiment_service import get_sentiment_service

router = APIRouter()


class ResponseCreate(BaseModel):
    campaign_id: str
    agent_id: str
    respondent_id: str
    question_id: str
    respuesta: Union[str, int, float]
    canal: str  # "voice", "whatsapp", "facebook", "instagram"
    duracion_segundos: Optional[int] = None


# ============ INGEST MODELS ============

class SentimentIngest(BaseModel):
    """
    Model for ingesting sentiment data from surveys.
    Used by mock_data_stream.py and real survey processing.
    """
    department_id: str = Field(..., description="ISO 3166-2:PY code (e.g., 'PY-ASU', 'PY-1')")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score between -1 and 1")
    department_name: Optional[str] = Field(None, description="Human-readable department name")
    region: Optional[str] = Field(None, description="Region: Oriental, Occidental, or Capital")
    topic: Optional[str] = Field(None, description="Survey topic/theme")
    channel: Optional[str] = Field(None, description="Channel: voice, whatsapp, facebook, instagram")
    response_id: Optional[str] = Field(None, description="Unique response identifier")
    timestamp: Optional[str] = Field(None, description="ISO timestamp of original response")


class SentimentResponse(BaseModel):
    """Response model for sentiment operations."""
    success: bool
    department_id: str
    average: float
    total_count: int
    message: str


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


# ============ REAL-TIME INGEST ENDPOINT ============

@router.post("/ingest", response_model=SentimentResponse)
async def ingest_sentiment(data: SentimentIngest):
    """
    Ingest a sentiment data point from a survey response.

    This endpoint:
    1. Validates the department ID (ISO 3166-2:PY)
    2. Updates the running average in Redis
    3. Broadcasts the update via WebSocket to connected clients

    The frontend map will automatically update to reflect the new sentiment.
    """
    service = get_sentiment_service()

    # Build metadata from optional fields
    metadata = {}
    if data.department_name:
        metadata["name"] = data.department_name
    if data.region:
        metadata["region"] = data.region
    if data.topic:
        metadata["topic"] = data.topic
    if data.channel:
        metadata["channel"] = data.channel
    if data.response_id:
        metadata["response_id"] = data.response_id
    if data.timestamp:
        metadata["original_timestamp"] = data.timestamp

    try:
        result = await service.record_sentiment(
            department_id=data.department_id,
            sentiment_score=data.sentiment_score,
            metadata=metadata if metadata else None,
        )

        return SentimentResponse(
            success=True,
            department_id=data.department_id,
            average=result["average"],
            total_count=result["total_count"],
            message=f"Sentiment recorded for {data.department_id}",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record sentiment: {e}")


@router.get("/sentiment/all")
async def get_all_sentiments():
    """
    Get current sentiment averages for all departments.

    Returns:
        Dict mapping department IDs (PY-XX) to sentiment averages (-1 to 1)
    """
    service = get_sentiment_service()
    sentiments = await service.get_all_sentiments()

    return {
        "sentiments": sentiments,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/sentiment/stats")
async def get_sentiment_stats():
    """Get overall sentiment statistics."""
    service = get_sentiment_service()
    stats = await service.get_stats()
    return stats


@router.get("/sentiment/{department_id}")
async def get_department_sentiment(department_id: str):
    """
    Get sentiment data for a specific department.

    Args:
        department_id: ISO 3166-2:PY code (e.g., "PY-ASU", "PY-11")
    """
    service = get_sentiment_service()

    try:
        data = await service.get_department_sentiment(department_id)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sentiment/{department_id}/history")
async def get_department_history(
    department_id: str,
    limit: int = 50,
):
    """
    Get recent sentiment history for a department.

    Args:
        department_id: ISO 3166-2:PY code
        limit: Maximum number of history items (default 50)
    """
    service = get_sentiment_service()

    try:
        history = await service.get_department_history(department_id, limit)
        return {
            "department_id": department_id,
            "history": history,
            "count": len(history),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sentiment/reset")
async def reset_all_sentiments():
    """
    Reset all sentiment data. USE WITH CAUTION.

    This is primarily for development/testing purposes.
    """
    service = get_sentiment_service()
    await service.reset_all()
    return {"success": True, "message": "All sentiment data has been reset"}
