"""Application configuration using Pydantic Settings"""
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List
import sys


DEFAULT_SECRET_KEY = "your-secret-key-change-in-production-use-openssl-rand-hex-32"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/graphene_trace"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = DEFAULT_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Application
    APP_NAME: str = "Graphene Trace API"
    DEBUG: bool = True

    @model_validator(mode='after')
    def validate_secret_key(self) -> 'Settings':
        """Ensure SECRET_KEY is changed from default when DEBUG is off"""
        # Runs after all fields are set, so DEBUG is reliably available
        if self.SECRET_KEY == DEFAULT_SECRET_KEY:
            if not self.DEBUG:
                raise ValueError(
                    "SECRET_KEY must be changed from default value in production. "
                    "Generate a secure key with: openssl rand -hex 32"
                )
            print("WARNING: Using default SECRET_KEY in DEBUG mode. Change this in production!", file=sys.stderr)

        # Ensure key is at least 32 characters
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")

        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
