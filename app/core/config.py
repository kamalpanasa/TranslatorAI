import json
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Environment
    ENV: str = "development"

    # API
    API_V1_STR: str = "/api/v1"

    # CORS Origins
    # Supports:
    # *
    # http://localhost:3000,http://localhost:5173
    # ["http://localhost:3000","http://localhost:5173"]
    BACKEND_CORS_ORIGINS: str = "*"

    # Security & Authentication
    JWT_SECRET: str = "dev-secret-key-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/app_db"
    )

    # File Uploads
    MAX_FILE_SIZE_MB: int = 10

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def cors_origins(self) -> List[str]:
        """
        Converts BACKEND_CORS_ORIGINS into a list.

        Supported formats:
        *
        http://localhost:3000,http://localhost:5173
        ["http://localhost:3000","http://localhost:5173"]
        """
        value = self.BACKEND_CORS_ORIGINS.strip()

        if not value:
            return []

        if value == "*":
            return ["*"]

        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(origin).strip() for origin in parsed]
            except json.JSONDecodeError:
                pass

        return [origin.strip() for origin in value.split(",") if origin.strip()]


# Initialize configuration
settings = Settings()