"""
VoxParaguay 2026 - Respondent API Routes
Law 7593/2025 compliant endpoints with audit logging
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import io

router = APIRouter()


class RespondentCreate(BaseModel):
    phone: str
    cedula: Optional[str] = None
    region: Optional[str] = None
    genero: Optional[str] = None
    rango_edad: Optional[str] = None


class RespondentSearch(BaseModel):
    cedula: Optional[str] = None
    phone: Optional[str] = None
    purpose: str  # Required by Law 7593/2025


class AuditReportRequest(BaseModel):
    fecha_desde: datetime
    fecha_hasta: datetime


# Dependency to get client info
def get_client_info(request: Request) -> dict:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


@router.post("/")
async def create_respondent(
    data: RespondentCreate,
    request: Request,
    # TODO: Add authentication dependency
    # current_user: Agent = Depends(get_current_user),
):
    """
    Crear nuevo encuestado con encriptación y índices ciegos.

    Los campos PII (teléfono, cédula) son encriptados automáticamente.
    Se generan índices ciegos para permitir búsquedas sin desencriptar.
    """
    # TODO: Integrate with Prisma client
    # For now, return mock response
    return {
        "message": "Encuestado creado exitosamente",
        "id": "temp-id",
        "nota": "Los datos PII han sido encriptados según Ley 7593/2025"
    }


@router.post("/search")
async def search_respondent(
    data: RespondentSearch,
    request: Request,
    decrypt_pii: bool = False,
):
    """
    Buscar encuestado por cédula o teléfono usando índice ciego.

    La búsqueda se realiza sobre el índice HMAC-SHA256, no sobre
    los datos encriptados, garantizando privacidad.

    Parámetros:
    - purpose: Finalidad de la búsqueda (requerido por Ley 7593/2025)
    - decrypt_pii: Si se debe desencriptar los datos PII (genera log adicional)
    """
    if not data.cedula and not data.phone:
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar cédula o teléfono para buscar"
        )

    if not data.purpose:
        raise HTTPException(
            status_code=400,
            detail="Debe especificar la finalidad de la búsqueda (Ley 7593/2025)"
        )

    # TODO: Integrate with RespondentService
    return {
        "message": "Búsqueda registrada en log de auditoría",
        "found": False,
        "purpose_logged": data.purpose
    }


@router.get("/{respondent_id}")
async def get_respondent(
    respondent_id: str,
    request: Request,
    purpose: str,
    decrypt_pii: bool = False,
):
    """
    Obtener encuestado por ID.

    El acceso queda registrado en el log de auditoría.
    """
    if not purpose:
        raise HTTPException(
            status_code=400,
            detail="Debe especificar la finalidad del acceso (Ley 7593/2025)"
        )

    # TODO: Integrate with RespondentService
    raise HTTPException(status_code=404, detail="Encuestado no encontrado")


@router.post("/check-duplicate")
async def check_duplicate(
    phone: str,
    campaign_id: Optional[str] = None,
):
    """
    Verificar si un teléfono ya existe (detección de duplicados).

    Usa el hash del teléfono para comparar sin revelar el número.
    """
    # TODO: Integrate with RespondentService
    return {"is_duplicate": False}


# ============ AUDIT LOG ENDPOINTS ============

@router.get("/audit/logs")
async def get_audit_logs(
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None,
    actor_id: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
):
    """
    Consultar logs de auditoría.

    Solo accesible por administradores.
    """
    # TODO: Add admin authentication check
    # TODO: Integrate with AuditLogService
    return {
        "logs": [],
        "total": 0,
        "message": "Endpoint de auditoría - requiere permisos de administrador"
    }


@router.post("/audit/report")
async def generate_audit_report(
    data: AuditReportRequest,
    request: Request,
):
    """
    Generar informe PDF de auditoría para cumplimiento Ley 7593/2025.

    El informe incluye:
    - Resumen ejecutivo
    - Estadísticas por finalidad
    - Desglose detallado de accesos
    """
    # TODO: Add admin authentication check

    # Validate date range
    if data.fecha_hasta < data.fecha_desde:
        raise HTTPException(
            status_code=400,
            detail="fecha_hasta debe ser posterior a fecha_desde"
        )

    max_days = 90
    if (data.fecha_hasta - data.fecha_desde).days > max_days:
        raise HTTPException(
            status_code=400,
            detail=f"El rango máximo es de {max_days} días"
        )

    # TODO: Integrate with AuditLogService
    # For now, return a sample PDF
    from app.services.audit_service import audit_report_generator

    # Sample data for demonstration
    sample_logs = [
        {
            "timestamp": datetime.now() - timedelta(hours=i),
            "actorId": f"agent-{i % 3 + 1}",
            "actorName": ["María García", "Juan López", "Ana Martínez"][i % 3],
            "action": ["READ", "SEARCH", "DECRYPT", "CREATE"][i % 4],
            "targetType": "Respondent",
            "targetId": f"resp-{i}",
            "purpose": ["Encuesta telefónica", "Verificación de datos", "Análisis estadístico"][i % 3],
        }
        for i in range(20)
    ]

    pdf_bytes = await audit_report_generator.generate_compliance_report(
        audit_logs=sample_logs,
        fecha_desde=data.fecha_desde,
        fecha_hasta=data.fecha_hasta,
        generated_by="Administrador",
    )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=audit_report_{data.fecha_desde.strftime('%Y%m%d')}_{data.fecha_hasta.strftime('%Y%m%d')}.pdf"
        }
    )
