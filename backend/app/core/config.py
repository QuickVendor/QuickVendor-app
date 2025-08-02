from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - PostgreSQL URL
    DATABASE_URL: str = "postgresql://username:password@localhost/quickvendor"
    
    class Config:
        env_file = ".env"


settings = Settings()
