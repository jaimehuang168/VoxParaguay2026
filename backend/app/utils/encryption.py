"""
VoxParaguay 2026 - Field-Level Encryption Utility
Compliant with Paraguay Law 7593/2025

Uses AES-256-GCM for encrypting PII fields:
- cedula (National ID)
- phone (Phone number)
- Any other personally identifiable information
"""

import base64
import hashlib
import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings


class EncryptionError(Exception):
    """Custom exception for encryption operations."""
    pass


class FieldEncryptor:
    """
    AES-256-GCM encryption for PII fields.
    Compliant with Paraguay Law 7593/2025.
    """

    def __init__(self, key: Optional[str] = None):
        """
        Initialize encryptor with a 32-byte key.

        Args:
            key: Base64-encoded 32-byte key. If not provided, uses settings.
        """
        key_b64 = key or settings.ENCRYPTION_KEY
        if not key_b64:
            raise EncryptionError(
                "ENCRYPTION_KEY no configurada. "
                "Requerido por Ley 7593/2025 de Paraguay."
            )

        try:
            self._key = base64.b64decode(key_b64)
            if len(self._key) != 32:
                raise EncryptionError(
                    "La clave debe ser de 32 bytes (256 bits) para AES-256."
                )
            self._aesgcm = AESGCM(self._key)
        except Exception as e:
            raise EncryptionError(f"Error inicializando encriptación: {e}")

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a string value.

        Args:
            plaintext: The string to encrypt

        Returns:
            Base64-encoded encrypted value (nonce + ciphertext + tag)
        """
        if not plaintext:
            return ""

        try:
            # Generate random 12-byte nonce (IV)
            nonce = os.urandom(12)

            # Encrypt
            ciphertext = self._aesgcm.encrypt(
                nonce,
                plaintext.encode('utf-8'),
                None  # No additional authenticated data
            )

            # Combine nonce + ciphertext and encode
            encrypted = nonce + ciphertext
            return base64.b64encode(encrypted).decode('utf-8')

        except Exception as e:
            raise EncryptionError(f"Error encriptando: {e}")

    def decrypt(self, ciphertext_b64: str) -> str:
        """
        Decrypt an encrypted value.

        Args:
            ciphertext_b64: Base64-encoded encrypted value

        Returns:
            Decrypted plaintext string
        """
        if not ciphertext_b64:
            return ""

        try:
            # Decode from base64
            encrypted = base64.b64decode(ciphertext_b64)

            # Extract nonce (first 12 bytes) and ciphertext
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]

            # Decrypt
            plaintext = self._aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext.decode('utf-8')

        except Exception as e:
            raise EncryptionError(f"Error desencriptando: {e}")

    def hash_for_comparison(self, value: str) -> str:
        """
        Create a deterministic hash for duplicate detection.
        Uses SHA-256 with the encryption key as salt.

        Args:
            value: The value to hash

        Returns:
            Hex-encoded hash string
        """
        if not value:
            return ""

        # Use key as salt for deterministic hashing
        salted = self._key + value.encode('utf-8')
        return hashlib.sha256(salted).hexdigest()


# Singleton instance
_encryptor: Optional[FieldEncryptor] = None


def get_encryptor() -> FieldEncryptor:
    """Get or create the singleton encryptor instance."""
    global _encryptor
    if _encryptor is None:
        _encryptor = FieldEncryptor()
    return _encryptor


def encrypt_cedula(cedula: str) -> str:
    """Encrypt a Paraguay national ID (cédula)."""
    return get_encryptor().encrypt(cedula)


def decrypt_cedula(encrypted_cedula: str) -> str:
    """Decrypt a Paraguay national ID (cédula)."""
    return get_encryptor().decrypt(encrypted_cedula)


def encrypt_phone(phone: str) -> str:
    """Encrypt a phone number."""
    return get_encryptor().encrypt(phone)


def decrypt_phone(encrypted_phone: str) -> str:
    """Decrypt a phone number."""
    return get_encryptor().decrypt(encrypted_phone)


def hash_phone_for_duplicate_check(phone: str) -> str:
    """
    Create hash of phone number for duplicate detection.
    Allows checking if same phone participated in campaign
    without storing the actual phone number.
    """
    return get_encryptor().hash_for_comparison(phone)


def generate_encryption_key() -> str:
    """
    Generate a new random 256-bit encryption key.
    Use this to create the ENCRYPTION_KEY environment variable.
    """
    key = os.urandom(32)
    return base64.b64encode(key).decode('utf-8')


# Anonymization utilities

def anonymize_respondent_data(data: dict) -> dict:
    """
    Remove all PII from respondent data before analysis.
    Required by Law 7593/2025 before data enters analysis modules.

    Args:
        data: Dictionary containing respondent data

    Returns:
        Anonymized dictionary safe for analysis
    """
    pii_fields = [
        'cedula', 'cedula_encrypted',
        'phone', 'phone_encrypted', 'telefono',
        'nombre', 'name', 'apellido',
        'email', 'direccion', 'address',
    ]

    anonymized = {}
    for key, value in data.items():
        if key.lower() not in [f.lower() for f in pii_fields]:
            anonymized[key] = value

    return anonymized
