from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # Storage
    S3_BUCKET_NAME: str
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_ENDPOINT_URL: str | None = None
    
    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Match Settings
    NORMAL_MODE_TIMEOUT_MINUTES: int = 2
    LONG_MODE_TIMEOUT_HOURS: int = 6
    GPS_RADIUS_MILES: float = 1.0
    
    # Video Settings
    MAX_CLIP_DURATION_SECONDS: int = 30
    MAX_CLIP_SIZE_MB: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
