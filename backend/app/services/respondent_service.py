"""
VoxParaguay 2026 - Respondent Service
Handles respondent CRUD with encryption, blind index, and audit logging

Law 7593/2025 Compliance:
- All PII fields are encrypted (AES-256-GCM)
- Blind indexes enable search without decryption
- All access is logged for audit purposes
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from prisma import Prisma

from app.utils.security import (
    encrypt_with_rotation,
    decrypt_with_rotation,
    create_cedula_index,
    create_phone_index,
    get_key_manager,
)
from app.utils.encryption import hash_phone_for_duplicate_check


class RespondentService:
    """
    Service layer for Respondent operations with full security compliance.
    """

    def __init__(self, db: Prisma):
        self.db = db

    async def create_respondent(
        self,
        phone: str,
        cedula: Optional[str] = None,
        region: Optional[str] = None,
        genero: Optional[str] = None,
        rango_edad: Optional[str] = None,
        actor_id: str = "sistema",
        actor_name: str = "Sistema",
        purpose: str = "Registro de nuevo encuestado",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new respondent with encrypted fields and blind indexes.

        Args:
            phone: Phone number (will be encrypted)
            cedula: National ID (will be encrypted)
            region: Geographic region
            genero: Gender
            rango_edad: Age range
            actor_id: ID of user creating the record
            actor_name: Name of user for audit log
            purpose: Purpose for audit log
            ip_address: Request IP for audit
            user_agent: Request user agent for audit

        Returns:
            Created respondent data (without decrypted PII)
        """
        # Encrypt PII fields
        phone_encrypted = encrypt_with_rotation(phone)
        cedula_encrypted = encrypt_with_rotation(cedula) if cedula else None

        # Generate blind indexes for search
        phone_index = create_phone_index(phone)
        cedula_index = create_cedula_index(cedula) if cedula else None

        # Generate hash for duplicate detection
        phone_hash = hash_phone_for_duplicate_check(phone)

        # Create respondent
        respondent = await self.db.respondent.create(
            data={
                "phoneEncrypted": phone_encrypted,
                "cedulaEncrypted": cedula_encrypted,
                "phoneHash": phone_hash,
                "phoneIndex": phone_index,
                "cedulaIndex": cedula_index,
                "region": region,
                "genero": genero,
                "rangoEdad": rango_edad,
            }
        )

        # Log the creation
        await self._log_access(
            actor_id=actor_id,
            actor_name=actor_name,
            action="CREATE",
            target_type="Respondent",
            target_id=respondent.id,
            purpose=purpose,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return {
            "id": respondent.id,
            "region": respondent.region,
            "genero": respondent.genero,
            "rangoEdad": respondent.rangoEdad,
            "createdAt": respondent.createdAt,
        }

    async def find_by_cedula(
        self,
        cedula: str,
        actor_id: str,
        actor_name: str,
        purpose: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        decrypt_pii: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Find respondent by cédula using blind index.

        Args:
            cedula: National ID to search
            actor_id: ID of user searching
            actor_name: Name of user for audit
            purpose: Justification for search (required by law)
            decrypt_pii: Whether to decrypt PII fields
            ip_address: Request IP
            user_agent: Request user agent

        Returns:
            Respondent data or None
        """
        # Generate blind index for search
        cedula_index = create_cedula_index(cedula)

        # Search using index (not encrypted value)
        respondent = await self.db.respondent.find_first(
            where={"cedulaIndex": cedula_index}
        )

        if not respondent:
            return None

        # Log the search
        await self._log_access(
            actor_id=actor_id,
            actor_name=actor_name,
            action="SEARCH",
            target_type="Respondent",
            target_id=respondent.id,
            purpose=purpose,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        result = {
            "id": respondent.id,
            "region": respondent.region,
            "genero": respondent.genero,
            "rangoEdad": respondent.rangoEdad,
            "createdAt": respondent.createdAt,
        }

        # Optionally decrypt PII (with additional logging)
        if decrypt_pii:
            await self._log_access(
                actor_id=actor_id,
                actor_name=actor_name,
                action="DECRYPT",
                target_type="Respondent",
                target_id=respondent.id,
                purpose=f"Desencriptación para: {purpose}",
                ip_address=ip_address,
                user_agent=user_agent,
            )

            result["cedula"] = decrypt_with_rotation(respondent.cedulaEncrypted) if respondent.cedulaEncrypted else None
            result["phone"] = decrypt_with_rotation(respondent.phoneEncrypted)

        return result

    async def find_by_phone(
        self,
        phone: str,
        actor_id: str,
        actor_name: str,
        purpose: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        decrypt_pii: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Find respondent by phone using blind index.
        """
        # Generate blind index for search
        phone_index = create_phone_index(phone)

        # Search using index
        respondent = await self.db.respondent.find_first(
            where={"phoneIndex": phone_index}
        )

        if not respondent:
            return None

        # Log the search
        await self._log_access(
            actor_id=actor_id,
            actor_name=actor_name,
            action="SEARCH",
            target_type="Respondent",
            target_id=respondent.id,
            purpose=purpose,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        result = {
            "id": respondent.id,
            "region": respondent.region,
            "genero": respondent.genero,
            "rangoEdad": respondent.rangoEdad,
            "createdAt": respondent.createdAt,
        }

        if decrypt_pii:
            await self._log_access(
                actor_id=actor_id,
                actor_name=actor_name,
                action="DECRYPT",
                target_type="Respondent",
                target_id=respondent.id,
                purpose=f"Desencriptación para: {purpose}",
                ip_address=ip_address,
                user_agent=user_agent,
            )

            result["cedula"] = decrypt_with_rotation(respondent.cedulaEncrypted) if respondent.cedulaEncrypted else None
            result["phone"] = decrypt_with_rotation(respondent.phoneEncrypted)

        return result

    async def get_by_id(
        self,
        respondent_id: str,
        actor_id: str,
        actor_name: str,
        purpose: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        decrypt_pii: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Get respondent by ID with audit logging.
        """
        respondent = await self.db.respondent.find_unique(
            where={"id": respondent_id}
        )

        if not respondent:
            return None

        # Log the read
        await self._log_access(
            actor_id=actor_id,
            actor_name=actor_name,
            action="READ",
            target_type="Respondent",
            target_id=respondent.id,
            purpose=purpose,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        result = {
            "id": respondent.id,
            "region": respondent.region,
            "genero": respondent.genero,
            "rangoEdad": respondent.rangoEdad,
            "createdAt": respondent.createdAt,
        }

        if decrypt_pii:
            await self._log_access(
                actor_id=actor_id,
                actor_name=actor_name,
                action="DECRYPT",
                target_type="Respondent",
                target_id=respondent.id,
                purpose=f"Desencriptación para: {purpose}",
                ip_address=ip_address,
                user_agent=user_agent,
            )

            result["cedula"] = decrypt_with_rotation(respondent.cedulaEncrypted) if respondent.cedulaEncrypted else None
            result["phone"] = decrypt_with_rotation(respondent.phoneEncrypted)

        return result

    async def check_duplicate(
        self,
        phone: str,
        campaign_id: Optional[str] = None,
    ) -> bool:
        """
        Check if phone number already exists (for duplicate detection).
        Uses phone_hash for comparison without decryption.
        """
        phone_hash = hash_phone_for_duplicate_check(phone)

        respondent = await self.db.respondent.find_unique(
            where={"phoneHash": phone_hash}
        )

        if not respondent:
            return False

        # If campaign_id provided, check if participated in that campaign
        if campaign_id:
            session = await self.db.surveysession.find_first(
                where={
                    "respondentId": respondent.id,
                    "campaignId": campaign_id,
                }
            )
            return session is not None

        return True

    async def _log_access(
        self,
        actor_id: str,
        actor_name: str,
        action: str,
        target_type: str,
        target_id: str,
        purpose: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict] = None,
    ) -> None:
        """
        Log access to PII data for Law 7593/2025 compliance.
        """
        await self.db.auditlog.create(
            data={
                "actorId": actor_id,
                "actorName": actor_name,
                "action": action,
                "targetType": target_type,
                "targetId": target_id,
                "purpose": purpose,
                "ipAddress": ip_address,
                "userAgent": user_agent,
                "details": details,
            }
        )


class AuditLogService:
    """
    Service for querying audit logs and generating reports.
    """

    def __init__(self, db: Prisma):
        self.db = db

    async def get_logs(
        self,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        actor_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs with filters.
        """
        where = {}

        if fecha_desde or fecha_hasta:
            where["timestamp"] = {}
            if fecha_desde:
                where["timestamp"]["gte"] = fecha_desde
            if fecha_hasta:
                where["timestamp"]["lte"] = fecha_hasta

        if actor_id:
            where["actorId"] = actor_id

        if action:
            where["action"] = action

        logs = await self.db.auditlog.find_many(
            where=where,
            order={"timestamp": "desc"},
            take=limit,
        )

        return [
            {
                "id": log.id,
                "timestamp": log.timestamp,
                "actorId": log.actorId,
                "actorName": log.actorName,
                "action": log.action,
                "targetType": log.targetType,
                "targetId": log.targetId,
                "purpose": log.purpose,
                "ipAddress": log.ipAddress,
                "userAgent": log.userAgent,
            }
            for log in logs
        ]

    async def generate_compliance_report(
        self,
        fecha_desde: datetime,
        fecha_hasta: datetime,
        generated_by: str = "Sistema",
    ) -> bytes:
        """
        Generate PDF compliance report for the specified period.
        """
        from app.services.audit_service import audit_report_generator

        logs = await self.get_logs(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            limit=10000,  # Get all logs for report
        )

        return await audit_report_generator.generate_compliance_report(
            audit_logs=logs,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            generated_by=generated_by,
        )
