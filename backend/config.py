from pydantic_settings import BaseSettings
from typing import List
import os
import secrets


class Settings(BaseSettings):
    # App
    app_name: str = "FinanceAI"
    app_env: str = "development"

    # LLM
    llm_provider: str = "openai"
    openai_api_key: str = ""
    gemini_api_key: str = ""

    # Database
    database_url: str = "sqlite:///./financial_analyst.db"

    # Redis (optional — only needed for Docker deployment)
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = secrets.token_hex(32)   # safe fallback; override in prod
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440   # 24h

    # API
    api_base_url: str = "http://localhost:8000"
    backend_cors_origins: List[str] = ["http://localhost:8501", "http://localhost:5173"]

    # Files
    max_upload_size_mb: int = 50
    upload_dir: str = "./uploads"

    # Rate limiting
    rate_limit_per_minute: int = 60
    llm_rate_limit_per_hour: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url


settings = Settings()

os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(os.path.join(settings.upload_dir, "reports"), exist_ok=True)
