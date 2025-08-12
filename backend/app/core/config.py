from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # JWT Settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Database - SQLite for development, PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./quickvendor.db"
    
    # Base URL for image serving (production: full backend URL)
    BASE_URL: Optional[str] = None  # e.g., https://quickvendor-backend.onrender.com
    
    # Sentry Configuration
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_SAMPLE_RATE: float = 1.0
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    
    # Slack Integration
    SLACK_WEBHOOK_URL: Optional[str] = None
    FEEDBACK_SECRET_KEY: Optional[str] = None
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    
    class Config:
        env_file = ".env"


settings = Settings()
