"""
VoxParaguay 2026 - Advanced Security Module
Compliant with Paraguay Law 7593/2025

Features:
- Key Rotation Manager: Supports multiple key versions (v1, v2)
- Blind Index Search: HMAC-SHA256 for searchable encryption
- Automatic version detection during decryption
"""

import base64
import hashlib
import hmac
import os
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.core.config import settings


class SecurityError(Exception):
    """Custom exception for security operations."""
    pass


# ============ KEY ROTATION MANAGER ============

class KeyRotationManager:
    """
    Manages multiple encryption key versions for seamless key rotation.

    Storage format: "version:base64(nonce+ciphertext)"
    Example: "v2:ABC123..."

    Supports:
    - v1: Original/legacy key (ENCRYPTION_KEY)
    - v2: New rotated key (ENCRYPTION_KEY_V2)
    """

    CURRENT_VERSION = "v2"

    def __init__(self):
        """Initialize with all available key versions."""
        self._keys = {}
        self._aesgcm_instances = {}

        # Load v1 key (required)
        v1_key = settings.ENCRYPTION_KEY
        if v1_key:
            self._keys["v1"] = base64.b64decode(v1_key)
            self._aesgcm_instances["v1"] = AESGCM(self._keys["v1"])

        # Load v2 key (optional, for rotation)
        v2_key = getattr(settings, 'ENCRYPTION_KEY_V2', None)
        if v2_key:
            self._keys["v2"] = base64.b64decode(v2_key)
            self._aesgcm_instances["v2"] = AESGCM(self._keys["v2"])
        else:
            # If no v2 key, use v1 as current
            self._keys["v2"] = self._keys.get("v1")
            self._aesgcm_instances["v2"] = self._aesgcm_instances.get("v1")

        if not self._keys.get("v1"):
            raise SecurityError(
                "ENCRYPTION_KEY no configurada. "
                "Requerido por Ley 7593/2025 de Paraguay."
            )

    def encrypt(self, plaintext: str, version: str = None) -> str:
        """
        Encrypt using the specified or current key version.

        Args:
            plaintext: String to encrypt
            version: Key version to use (default: CURRENT_VERSION)

        Returns:
            Encrypted string in format "version:base64(nonce+ciphertext)"
        """
        if not plaintext:
            return ""

        version = version or self.CURRENT_VERSION

        if version not in self._aesgcm_instances:
            raise SecurityError(f"Versión de clave '{version}' no disponible")

        try:
            # Generate random 12-byte nonce
            nonce = os.urandom(12)

            # Encrypt with specified version
            aesgcm = self._aesgcm_instances[version]
            ciphertext = aesgcm.encrypt(
                nonce,
                plaintext.encode('utf-8'),
                None
            )

            # Combine and encode
            encrypted = nonce + ciphertext
            encoded = base64.b64encode(encrypted).decode('utf-8')

            # Return with version prefix
            return f"{version}:{encoded}"

        except Exception as e:
            raise SecurityError(f"Error encriptando: {e}")

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt automatically detecting the key version.

        Args:
            ciphertext: Encrypted string (with or without version prefix)

        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ""

        try:
            # Detect version from prefix
            version, encrypted_data = self._parse_versioned_ciphertext(ciphertext)

            if version not in self._aesgcm_instances:
                raise SecurityError(f"Versión de clave '{version}' no disponible")

            # Decode from base64
            encrypted = base64.b64decode(encrypted_data)

            # Extract nonce and ciphertext
            nonce = encrypted[:12]
            ct = encrypted[12:]

            # Decrypt with appropriate key version
            aesgcm = self._aesgcm_instances[version]
            plaintext = aesgcm.decrypt(nonce, ct, None)

            return plaintext.decode('utf-8')

        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(f"Error desencriptando: {e}")

    def _parse_versioned_ciphertext(self, ciphertext: str) -> Tuple[str, str]:
        """
        Parse version prefix from ciphertext.

        Returns:
            Tuple of (version, encrypted_data)
        """
        if ":" in ciphertext:
            parts = ciphertext.split(":", 1)
            if parts[0] in self._keys:
                return parts[0], parts[1]

        # Legacy format without version prefix - assume v1
        return "v1", ciphertext

    def re_encrypt(self, ciphertext: str, target_version: str = None) -> str:
        """
        Re-encrypt data with a new key version (for key rotation).

        Args:
            ciphertext: Currently encrypted data
            target_version: Target key version (default: CURRENT_VERSION)

        Returns:
            Re-encrypted data with new version
        """
        target_version = target_version or self.CURRENT_VERSION
        plaintext = self.decrypt(ciphertext)
        return self.encrypt(plaintext, target_version)

    def get_current_version(self) -> str:
        """Get the current encryption version."""
        return self.CURRENT_VERSION

    def is_current_version(self, ciphertext: str) -> bool:
        """Check if ciphertext is encrypted with current version."""
        if not ciphertext:
            return True
        version, _ = self._parse_versioned_ciphertext(ciphertext)
        return version == self.CURRENT_VERSION

    # ============ TEST-COMPATIBLE ALIASES ============

    def encrypt_new(self, plaintext: str) -> str:
        """
        Encrypt using the current (latest) key version.
        Alias for encrypt() with default version.

        Args:
            plaintext: String to encrypt

        Returns:
            Encrypted string with current version prefix
        """
        return self.encrypt(plaintext, self.CURRENT_VERSION)

    def encrypt_with_version(self, plaintext: str, version: str) -> str:
        """
        Encrypt with a specific key version.
        Alias for encrypt() with explicit version.

        Args:
            plaintext: String to encrypt
            version: Key version to use (e.g., "v1", "v2")

        Returns:
            Encrypted string with version prefix
        """
        return self.encrypt(plaintext, version)

    def decrypt_any(self, ciphertext: str) -> str:
        """
        Decrypt with automatic version detection and error handling.
        Returns "ERROR_DECRYPTION" on failure instead of raising exception.

        Args:
            ciphertext: Encrypted string (any version)

        Returns:
            Decrypted plaintext or "ERROR_DECRYPTION" on failure
        """
        if not ciphertext:
            return ""

        try:
            return self.decrypt(ciphertext)
        except (SecurityError, Exception):
            return "ERROR_DECRYPTION"

    def rotate_data_task(self, encrypted_items: list) -> list:
        """
        Batch re-encrypt a list of encrypted items to current version.
        Used for key rotation migrations.

        Args:
            encrypted_items: List of encrypted strings (any version)

        Returns:
            List of re-encrypted strings with current version
        """
        result = []
        for item in encrypted_items:
            try:
                re_encrypted = self.re_encrypt(item, self.CURRENT_VERSION)
                result.append(re_encrypted)
            except (SecurityError, Exception):
                # Keep original if re-encryption fails
                result.append(item)
        return result


# ============ BLIND INDEX SEARCH SERVICE ============

class SearchService:
    """
    Blind Index implementation using HMAC-SHA256.

    Allows searching encrypted fields without decryption by creating
    deterministic indexes using an independent key.

    Security:
    - Uses separate BLIND_INDEX_KEY (not the encryption key)
    - Produces 64-character hex strings (256-bit)
    - Deterministic: same input always produces same index
    """

    def __init__(self, key: Optional[str] = None):
        """
        Initialize with blind index key.

        Args:
            key: Base64-encoded 32-byte key. If not provided, uses settings.
        """
        key_b64 = key or getattr(settings, 'BLIND_INDEX_KEY', None)

        if not key_b64:
            raise SecurityError(
                "BLIND_INDEX_KEY no configurada. "
                "Requerida para búsqueda segura según Ley 7593/2025."
            )

        try:
            self._key = base64.b64decode(key_b64)
            if len(self._key) != 32:
                raise SecurityError(
                    "BLIND_INDEX_KEY debe ser de 32 bytes (256 bits)."
                )
        except Exception as e:
            raise SecurityError(f"Error inicializando SearchService: {e}")

    def create_index(self, value: str) -> str:
        """
        Create a blind index for a value.

        Args:
            value: Plain text value to index

        Returns:
            64-character hex string (HMAC-SHA256)
        """
        if not value:
            return ""

        # Normalize value (lowercase, strip whitespace)
        normalized = value.strip().lower()

        # Create HMAC-SHA256
        h = hmac.new(
            self._key,
            normalized.encode('utf-8'),
            hashlib.sha256
        )

        return h.hexdigest()

    def create_cedula_index(self, cedula: str) -> str:
        """
        Create blind index for a cédula (national ID).

        Args:
            cedula: Paraguay national ID number

        Returns:
            64-character hex string
        """
        if not cedula:
            return ""

        # Normalize: remove dots, dashes, spaces
        normalized = ''.join(filter(str.isdigit, cedula))
        return self.create_index(normalized)

    def create_phone_index(self, phone: str) -> str:
        """
        Create blind index for a phone number.

        Args:
            phone: Phone number (any format)

        Returns:
            64-character hex string
        """
        if not phone:
            return ""

        # Normalize: remove all non-digits
        normalized = ''.join(filter(str.isdigit, phone))

        # Keep last 9 digits (Paraguay mobile format)
        if len(normalized) > 9:
            normalized = normalized[-9:]

        return self.create_index(normalized)

    def verify_index(self, value: str, index: str) -> bool:
        """
        Verify if a value matches a blind index.

        Args:
            value: Plain text value to check
            index: Existing blind index to compare

        Returns:
            True if value matches the index
        """
        if not value or not index:
            return False

        computed = self.create_index(value)
        return hmac.compare_digest(computed, index)


# ============ SINGLETON INSTANCES ============

_key_manager: Optional[KeyRotationManager] = None
_search_service: Optional[SearchService] = None


def get_key_manager() -> KeyRotationManager:
    """Get or create the singleton KeyRotationManager instance."""
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyRotationManager()
    return _key_manager


def get_search_service() -> SearchService:
    """Get or create the singleton SearchService instance."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service


# ============ CONVENIENCE FUNCTIONS ============

def encrypt_with_rotation(plaintext: str) -> str:
    """Encrypt using current key version with rotation support."""
    return get_key_manager().encrypt(plaintext)


def decrypt_with_rotation(ciphertext: str) -> str:
    """Decrypt automatically detecting key version."""
    return get_key_manager().decrypt(ciphertext)


def create_cedula_index(cedula: str) -> str:
    """Create blind index for cédula."""
    return get_search_service().create_cedula_index(cedula)


def create_phone_index(phone: str) -> str:
    """Create blind index for phone number."""
    return get_search_service().create_phone_index(phone)


def generate_blind_index_key() -> str:
    """Generate a new random 256-bit blind index key."""
    key = os.urandom(32)
    return base64.b64encode(key).decode('utf-8')
