"""
VoxParaguay 2026 - Configuration Settings
Compliant with Paraguay Law 7593/2025
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List, Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "VoxParaguay 2026"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://localhost:5432/voxparaguay"
    REDIS_URL: str = "redis://localhost:6379"

    # Encryption (Law 7593/2025 compliance)
    ENCRYPTION_KEY: str = ""      # v1 key - Must be 32-byte base64 encoded
    ENCRYPTION_KEY_V2: str = ""   # v2 key for rotation (optional)
    BLIND_INDEX_KEY: str = ""     # Independent key for searchable encryption

    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    # Meta (WhatsApp, Facebook, Instagram)
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_VERIFY_TOKEN: str = ""
    META_ACCESS_TOKEN: str = ""

    # Anthropic (Claude AI)
    ANTHROPIC_API_KEY: str = ""

    # Mapbox
    MAPBOX_ACCESS_TOKEN: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Paraguay Locale
    DEFAULT_LOCALE: str = "es-PY"
    TIMEZONE: str = "America/Asuncion"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
