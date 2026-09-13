from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MineGuard AI"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "mineguard-super-secret-jwt-signing-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./mineguard.db"

    # CORS (can be JSON array string or comma-separated string in env)
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    @property
    def cors_origins(self) -> List[str]:
        if isinstance(self.BACKEND_CORS_ORIGINS, list):
            return self.BACKEND_CORS_ORIGINS
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            import json
            val = self.BACKEND_CORS_ORIGINS.strip()
            if val.startswith("["):
                try:
                    return json.loads(val)
                except Exception:
                    pass
            return [origin.strip() for origin in val.split(",") if origin.strip()]
        return []

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 15

    # OCR
    TESSERACT_CMD: str = ""

    # Integrations
    GEE_SERVICE_ACCOUNT: str = ""
    GEE_PRIVATE_KEY_PATH: str = ""
    FIREBASE_CREDENTIALS_PATH: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
