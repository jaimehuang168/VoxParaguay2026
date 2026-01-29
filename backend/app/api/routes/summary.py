"""
VoxParaguay 2026 - AI Summary Routes
Claude 3.5 API integration for department sentiment analysis

Compliance: This module implements PII protection per Paraguay Law 7593/2025.
All respondent data is anonymized before being sent to the AI model.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from anthropic import Anthropic

from app.core.config import settings
from app.services.sentiment_service import get_sentiment_service
from app.utils.encryption import anonymize_respondent_data

router = APIRouter()


# ============ DEPARTMENT METADATA ============

DEPARTMENT_INFO = {
    "PY-ASU": {"name": "Asunción", "capital": "Asunción", "region": "Capital", "population": 524190},
    "PY-1": {"name": "Concepción", "capital": "Concepción", "region": "Oriental", "population": 251438},
    "PY-2": {"name": "San Pedro", "capital": "San Pedro de Ycuamandiyú", "region": "Oriental", "population": 431802},
    "PY-3": {"name": "Cordillera", "capital": "Caacupé", "region": "Oriental", "population": 314768},
    "PY-4": {"name": "Guairá", "capital": "Villarrica", "region": "Oriental", "population": 227794},
    "PY-5": {"name": "Caaguazú", "capital": "Coronel Oviedo", "region": "Oriental", "population": 550152},
    "PY-6": {"name": "Caazapá", "capital": "Caazapá", "region": "Oriental", "population": 193938},
    "PY-7": {"name": "Itapúa", "capital": "Encarnación", "region": "Oriental", "population": 601120},
    "PY-8": {"name": "Misiones", "capital": "San Juan Bautista", "region": "Oriental", "population": 124999},
    "PY-9": {"name": "Paraguarí", "capital": "Paraguarí", "region": "Oriental", "population": 254411},
    "PY-10": {"name": "Alto Paraná", "capital": "Ciudad del Este", "region": "Oriental", "population": 822823},
    "PY-11": {"name": "Central", "capital": "Areguá", "region": "Oriental", "population": 2221792},
    "PY-12": {"name": "Ñeembucú", "capital": "Pilar", "region": "Oriental", "population": 88995},
    "PY-13": {"name": "Amambay", "capital": "Pedro Juan Caballero", "region": "Oriental", "population": 164614},
    "PY-14": {"name": "Canindeyú", "capital": "Salto del Guairá", "region": "Oriental", "population": 221824},
    "PY-15": {"name": "Presidente Hayes", "capital": "Villa Hayes", "region": "Occidental", "population": 121075},
    "PY-16": {"name": "Alto Paraguay", "capital": "Fuerte Olimpo", "region": "Occidental", "population": 17587},
    "PY-19": {"name": "Boquerón", "capital": "Filadelfia", "region": "Occidental", "population": 68050},
}

TOPIC_LABELS = {
    "economia": "Economía",
    "salud": "Salud Pública",
    "educacion": "Educación",
    "seguridad": "Seguridad Ciudadana",
    "infraestructura": "Infraestructura",
    "empleo": "Empleo y Trabajo",
    "corrupcion": "Corrupción y Transparencia",
    "medio_ambiente": "Medio Ambiente",
}


# ============ SYSTEM PROMPT ============

SOCIOLOGIST_SYSTEM_PROMPT = """Eres un sociólogo paraguayo experto en análisis de opinión pública y dinámica social.

PERFIL PROFESIONAL:
- Doctor en Sociología por la Universidad Nacional de Asunción
- Especialista en análisis de encuestas y percepción ciudadana
- 20 años de experiencia investigando la realidad social paraguaya
- Conocedor profundo de las diferencias regionales entre la Región Oriental y el Chaco

TU TAREA:
Analizar los datos de sentimiento de un departamento específico y producir un resumen ejecutivo profesional en español.

ESTRUCTURA DEL RESUMEN:
1. **Diagnóstico General** (2-3 oraciones): Evaluación del estado actual del sentimiento ciudadano
2. **Factores Explicativos** (2-3 puntos): Posibles causas socioeconómicas o políticas
3. **Tendencias Observadas**: Patrones en los datos
4. **Recomendaciones de Política Pública** (2-3 puntos): Sugerencias concretas para autoridades

ESTILO:
- Formal y académico, pero accesible
- Basado en evidencia (los datos proporcionados)
- Contextualizado en la realidad paraguaya actual
- Sin información personal de encuestados (CRÍTICO: nunca mencionar datos de identificación)

IMPORTANTE - CUMPLIMIENTO LEGAL:
- NUNCA menciones nombres, cédulas, teléfonos, direcciones u otros datos personales
- Solo trabajar con datos agregados y anonimizados
- Cualquier dato que parezca identificable debe ser omitido
- Cumplir con la Ley 7593/2025 de Protección de Datos Personales de Paraguay"""


# ============ RESPONSE MODELS ============

class SummaryResponse(BaseModel):
    """AI-generated department summary response."""
    department_id: str
    department_name: str
    region: str
    sentiment_average: Optional[float] = None
    total_responses: int = 0
    summary: str
    generated_at: str
    topics_analyzed: List[str] = []
    compliance_note: str = "Este resumen fue generado sin acceso a datos personales identificables."


class SummaryRequest(BaseModel):
    """Optional request body for customizing summary."""
    include_recommendations: bool = True
    language: str = "es"  # Always Spanish for this version
    max_length: int = Field(default=500, ge=100, le=2000)


# ============ PII COMPLIANCE CHECK ============

def verify_no_pii_in_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify and strip any potential PII from data before AI processing.
    Required for compliance with Paraguay Law 7593/2025.

    Args:
        data: Dictionary that might contain PII

    Returns:
        Sanitized dictionary safe for AI processing
    """
    # Use the existing anonymization utility
    sanitized = anonymize_respondent_data(data)

    # Additional checks for nested structures
    pii_patterns = [
        'cedula', 'phone', 'telefono', 'nombre', 'name',
        'email', 'direccion', 'address', 'apellido',
        'dni', 'ruc', 'passport', 'encrypted'
    ]

    def recursive_clean(obj, depth=0):
        if depth > 10:  # Prevent infinite recursion
            return obj

        if isinstance(obj, dict):
            return {
                k: recursive_clean(v, depth + 1)
                for k, v in obj.items()
                if not any(pii in k.lower() for pii in pii_patterns)
            }
        elif isinstance(obj, list):
            return [recursive_clean(item, depth + 1) for item in obj]
        else:
            return obj

    return recursive_clean(sanitized)


def build_ai_prompt(
    dept_id: str,
    dept_info: Dict[str, Any],
    sentiment_data: Dict[str, Any],
    topic_distribution: Dict[str, int],
) -> str:
    """
    Build the AI prompt with anonymized, aggregated data only.

    This function ensures NO PII is included in the prompt.
    """
    dept_name = dept_info.get("name", dept_id)
    region = dept_info.get("region", "Desconocido")
    population = dept_info.get("population", 0)
    capital = dept_info.get("capital", "N/A")

    avg_sentiment = sentiment_data.get("average")
    total_count = sentiment_data.get("total_count", 0)

    # Format sentiment interpretation
    if avg_sentiment is None:
        sentiment_desc = "sin datos suficientes"
    elif avg_sentiment >= 0.3:
        sentiment_desc = f"muy positivo ({avg_sentiment:.2f})"
    elif avg_sentiment >= 0.1:
        sentiment_desc = f"positivo ({avg_sentiment:.2f})"
    elif avg_sentiment >= -0.1:
        sentiment_desc = f"neutral ({avg_sentiment:.2f})"
    elif avg_sentiment >= -0.3:
        sentiment_desc = f"negativo ({avg_sentiment:.2f})"
    else:
        sentiment_desc = f"muy negativo ({avg_sentiment:.2f})"

    # Format topic distribution
    topics_text = ""
    if topic_distribution:
        sorted_topics = sorted(topic_distribution.items(), key=lambda x: x[1], reverse=True)
        topics_text = "\n".join([
            f"   - {TOPIC_LABELS.get(topic, topic)}: {count} menciones"
            for topic, count in sorted_topics[:5]
        ])

    prompt = f"""Analiza los siguientes datos agregados y anonimizados del departamento de {dept_name}, Paraguay:

DATOS DEL DEPARTAMENTO:
- Nombre: {dept_name}
- Código ISO: {dept_id}
- Región: {region}
- Capital: {capital}
- Población aproximada: {population:,} habitantes

DATOS DE SENTIMIENTO (AGREGADOS Y ANONIMIZADOS):
- Índice de sentimiento promedio: {sentiment_desc}
- Total de respuestas procesadas: {total_count}
- Fecha de análisis: {datetime.now().strftime('%d/%m/%Y')}

DISTRIBUCIÓN POR TEMAS:
{topics_text if topics_text else "   - Sin datos de temas disponibles"}

NOTA IMPORTANTE: Estos datos son completamente anónimos y agregados.
No contienen ni hacen referencia a ningún dato personal identificable.
Tu análisis debe basarse únicamente en estas estadísticas agregadas.

Por favor, genera un resumen ejecutivo siguiendo la estructura indicada en tus instrucciones."""

    return prompt


# ============ AI CLIENT ============

class AISummaryService:
    """Service for generating AI-powered department summaries."""

    def __init__(self):
        self._client: Optional[Anthropic] = None

    @property
    def client(self) -> Anthropic:
        if self._client is None:
            if not settings.ANTHROPIC_API_KEY:
                raise HTTPException(
                    status_code=503,
                    detail="Servicio de IA no configurado. Falta ANTHROPIC_API_KEY."
                )
            self._client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        return self._client

    async def generate_summary(
        self,
        dept_id: str,
        dept_info: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        topic_distribution: Dict[str, int],
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate AI summary for a department.

        Args:
            dept_id: Department ISO code
            dept_info: Department metadata
            sentiment_data: Anonymized sentiment statistics
            topic_distribution: Topic mention counts
            max_tokens: Maximum response length

        Returns:
            Generated summary text in Spanish
        """
        # Build prompt with anonymized data
        prompt = build_ai_prompt(
            dept_id=dept_id,
            dept_info=dept_info,
            sentiment_data=verify_no_pii_in_data(sentiment_data),
            topic_distribution=topic_distribution,
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                system=SOCIOLOGIST_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generando resumen: {str(e)}"
            )


# Singleton instance
_summary_service: Optional[AISummaryService] = None


def get_summary_service() -> AISummaryService:
    global _summary_service
    if _summary_service is None:
        _summary_service = AISummaryService()
    return _summary_service


# ============ API ENDPOINTS ============

@router.get("/{dept_id}", response_model=SummaryResponse)
async def get_department_summary(
    dept_id: str,
    include_recommendations: bool = True,
):
    """
    Generate an AI-powered summary for a specific department.

    This endpoint:
    1. Retrieves anonymized sentiment data from Redis
    2. Verifies no PII is included in the AI prompt
    3. Generates a professional summary using Claude 3.5
    4. Returns the summary with compliance metadata

    Args:
        dept_id: ISO 3166-2:PY department code (e.g., "PY-ASU", "PY-11")
        include_recommendations: Include policy recommendations (default: True)

    Returns:
        SummaryResponse with generated summary and metadata

    Compliance:
        This endpoint complies with Paraguay Law 7593/2025.
        No personal data is sent to the AI model.
    """
    # Validate department ID
    if dept_id not in DEPARTMENT_INFO:
        raise HTTPException(
            status_code=400,
            detail=f"Departamento inválido: {dept_id}. Use códigos ISO 3166-2:PY."
        )

    dept_info = DEPARTMENT_INFO[dept_id]

    # Get sentiment data from Redis
    sentiment_service = get_sentiment_service()
    sentiment_data = await sentiment_service.get_department_sentiment(dept_id)

    # Get topic distribution (mock for now - would come from database)
    # In production, this would aggregate from actual survey responses
    topic_distribution = await get_topic_distribution(dept_id)

    # Generate AI summary
    summary_service = get_summary_service()
    summary_text = await summary_service.generate_summary(
        dept_id=dept_id,
        dept_info=dept_info,
        sentiment_data=sentiment_data,
        topic_distribution=topic_distribution,
    )

    return SummaryResponse(
        department_id=dept_id,
        department_name=dept_info["name"],
        region=dept_info["region"],
        sentiment_average=sentiment_data.get("average"),
        total_responses=sentiment_data.get("total_count", 0),
        summary=summary_text,
        generated_at=datetime.now().isoformat(),
        topics_analyzed=list(topic_distribution.keys()) if topic_distribution else [],
        compliance_note="Este resumen fue generado con datos completamente anonimizados, "
                       "en cumplimiento con la Ley 7593/2025 de Paraguay.",
    )


@router.get("/{dept_id}/topics")
async def get_department_topics(dept_id: str):
    """
    Get topic distribution for a department.

    Args:
        dept_id: ISO 3166-2:PY department code
    """
    if dept_id not in DEPARTMENT_INFO:
        raise HTTPException(status_code=400, detail=f"Departamento inválido: {dept_id}")

    topics = await get_topic_distribution(dept_id)

    return {
        "department_id": dept_id,
        "topics": topics,
        "labels": {k: TOPIC_LABELS.get(k, k) for k in topics.keys()},
    }


async def get_topic_distribution(dept_id: str) -> Dict[str, int]:
    """
    Get topic mention distribution for a department.

    In production, this would query the database for actual topic counts.
    For now, returns simulated data based on sentiment history.
    """
    sentiment_service = get_sentiment_service()

    try:
        history = await sentiment_service.get_department_history(dept_id, limit=100)

        # Count topics from history metadata
        topic_counts: Dict[str, int] = {}
        for entry in history:
            if isinstance(entry, dict):
                metadata = entry.get("metadata", {})
                if metadata and isinstance(metadata, dict):
                    topic = metadata.get("topic")
                    if topic:
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1

        return topic_counts

    except Exception:
        # Return empty if no history available
        return {}


@router.get("/health")
async def summary_health_check():
    """Check if AI summary service is available."""
    try:
        service = get_summary_service()
        # Just check if client can be created
        _ = service.client
        return {
            "status": "healthy",
            "service": "ai-summary",
            "model": "claude-sonnet-4-20250514",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
