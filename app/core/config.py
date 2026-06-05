import os
import json
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Application Settings
    PROJECT_NAME: str = "Multilingual Translation API"
    ENV: str = "development"
    API_V1_STR: str = "/api/v1"
    
    # CORS Origins (stored as raw string to prevent pydantic-settings list-parsing exceptions)
    BACKEND_CORS_ORIGINS: str = "*"

    # Security & Authentication
    JWT_SECRET: str = "dev-secret-key-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # AI/ML Models
    NLLB_MODEL_NAME: str = "facebook/nllb-200-3.3B"
    WHISPER_MODEL_NAME: str = "base"

    # OCR Settings
    TESSERACT_CMD: str = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

    # Storage & Database (Supabase)
    SUPABASE_URL: str = "https://your-project-ref.supabase.co"
    SUPABASE_KEY: str = "your-anon-or-service-role-key"

    # Limits & Uploads
    MAX_FILE_SIZE_MB: int = 50

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def cors_origins(self) -> List[str]:
        """
        Parses the raw BACKEND_CORS_ORIGINS string into a list of origins.
        Supports:
          - Wildcard "*"
          - Comma-separated list "url1,url2"
          - JSON array '["url1", "url2"]'
          - Empty values (falls back to empty list)
        """
        v = self.BACKEND_CORS_ORIGINS.strip()
        if not v:
            return []
        if v.startswith("[") and v.endswith("]"):
            try:
                return json.loads(v)
            except Exception:
                pass
        return [i.strip() for i in v.split(",")]


# Initialize configuration
settings = Settings()
