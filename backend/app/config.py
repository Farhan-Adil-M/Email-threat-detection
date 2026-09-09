from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/sentinel"
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "dev-secret-change-in-production"
    DEMO_MODE: bool = False
    EVIDENCE_STORAGE_PATH: str = "./data/storage"
    MAX_UPLOAD_SIZE: int = 25 * 1024 * 1024  # 25 MB
    INTEL_MODE: str = "disabled"  # disabled | fixture | live
    INTEL_DNS_TIMEOUT: float = 2.0

    def get_database_url(self) -> str:
        return self.DATABASE_URL


settings = Settings()
