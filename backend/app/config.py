import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "InsureFlow"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres:postgres@localhost:5432/insureflow"
    )
    SQLITE_FALLBACK_URL: str = "sqlite:///./insureflow.db"
    
    # Synthetic Data Generator
    DATA_GEN_SEED: int = 20261022
    AUTO_SEED_ON_STARTUP: bool = True
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "*"
    ]
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
