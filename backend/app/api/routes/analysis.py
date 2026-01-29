"""
VoxParaguay 2026 - Análisis con Claude API
Generación de resúmenes en español paraguayo
"""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx

router = APIRouter()


class TemaData(BaseModel):
    tema: str
    menciones: int
    sentimiento: float


class AnalysisRequest(BaseModel):
    departamento: str
    capital: str
    poblacion: int
    encuestas_completadas: int
    sentimiento_promedio: float
    temas: List[TemaData]


class AnalysisResponse(BaseModel):
    resumen: str
    recomendaciones: List[str]
    departamento: str


CLAUDE_SYSTEM_PROMPT = """Eres un analista político y social experto en Paraguay.
Tu tarea es analizar datos de encuestas de opinión pública y generar resúmenes
ejecutivos en español paraguayo (ES-PY).

Reglas:
1. Usa español neutro pero con modismos paraguayos cuando sea apropiado
2. Sé conciso pero informativo (máximo 3 oraciones para el resumen)
3. Menciona los datos más relevantes
4. Ofrece 2-3 recomendaciones de políticas públicas basadas en los datos
5. Mantén un tono profesional y objetivo"""


@router.post("/department", response_model=AnalysisResponse)
async def analyze_department(request: AnalysisRequest):
    """
    Genera un análisis detallado de un departamento usando Claude API.
    Retorna un resumen en español paraguayo con recomendaciones.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        # Fallback a análisis local si no hay API key
        return generate_fallback_analysis(request)

    # Preparar prompt para Claude
    temas_text = "\n".join([
        f"- {t.tema}: {t.menciones} menciones, sentimiento {t.sentimiento*100:.0f}%"
        for t in request.temas
    ])

    user_prompt = f"""Analiza los siguientes datos de opinión pública del departamento de {request.departamento}, Paraguay:

**Información General:**
- Capital: {request.capital}
- Población: {request.poblacion:,}
- Encuestas completadas: {request.encuestas_completadas}
- Índice de sentimiento promedio: {request.sentimiento_promedio*100:.1f}%

**Temas Principales Mencionados:**
{temas_text}

Genera:
1. Un resumen ejecutivo de 2-3 oraciones
2. 3 recomendaciones de políticas públicas prioritarias

Responde en formato JSON con las claves "resumen" y "recomendaciones" (array de strings)."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1024,
                    "system": CLAUDE_SYSTEM_PROMPT,
                    "messages": [
                        {"role": "user", "content": user_prompt}
                    ],
                },
            )

            if response.status_code != 200:
                return generate_fallback_analysis(request)

            result = response.json()
            content = result.get("content", [{}])[0].get("text", "")

            # Parsear respuesta JSON de Claude
            import json
            try:
                # Buscar JSON en la respuesta
                start = content.find("{")
                end = content.rfind("}") + 1
                if start >= 0 and end > start:
                    parsed = json.loads(content[start:end])
                    return AnalysisResponse(
                        resumen=parsed.get("resumen", ""),
                        recomendaciones=parsed.get("recomendaciones", []),
                        departamento=request.departamento,
                    )
            except json.JSONDecodeError:
                pass

            # Si no se puede parsear, usar el contenido directo
            return AnalysisResponse(
                resumen=content[:500],
                recomendaciones=[],
                departamento=request.departamento,
            )

    except Exception as e:
        return generate_fallback_analysis(request)


def generate_fallback_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """Genera análisis sin usar Claude API (fallback)."""
    top_tema = request.temas[0] if request.temas else None
    negative_temas = [t for t in request.temas if t.sentimiento < 0]

    sentiment_word = (
        "positivo" if request.sentimiento_promedio > 0.1
        else "negativo" if request.sentimiento_promedio < -0.1
        else "neutral"
    )

    resumen = f"En {request.departamento}, el sentimiento ciudadano es predominantemente {sentiment_word} "
    resumen += f"con un índice de {request.sentimiento_promedio*100:.0f}%. "

    if top_tema:
        resumen += f"El tema más mencionado es \"{top_tema.tema}\" con {top_tema.menciones} referencias."

    recomendaciones = []
    for tema in negative_temas[:3]:
        if tema.sentimiento < -0.2:
            recomendaciones.append(
                f"Priorizar políticas de mejora en {tema.tema.lower()} "
                f"(sentimiento: {tema.sentimiento*100:.0f}%)"
            )

    if not recomendaciones:
        recomendaciones = [
            "Mantener las políticas actuales que generan satisfacción ciudadana",
            "Fortalecer la comunicación sobre logros en áreas bien valoradas",
        ]

    return AnalysisResponse(
        resumen=resumen,
        recomendaciones=recomendaciones,
        departamento=request.departamento,
    )


@router.get("/national-summary")
async def get_national_summary():
    """
    Obtiene un resumen nacional agregando datos de todos los departamentos.
    """
    # En producción, esto vendría de la base de datos
    return {
        "total_encuestas": 8934,
        "sentimiento_nacional": 0.12,
        "departamentos_positivos": 11,
        "departamentos_negativos": 6,
        "tema_nacional_principal": "Empleo y economía",
        "fecha_actualizacion": "2026-01-28T00:00:00Z",
    }
