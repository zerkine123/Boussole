# ============================================
# Boussole - Core Configuration
# ============================================

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # ============================================
    # Application Settings
    # ============================================
    APP_NAME: str = "Boussole"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Algerian Data Analytics SaaS Platform"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    
    # ============================================
    # Database Settings
    # ============================================
    DATABASE_URL: str = "postgresql+asyncpg://boussole:boussole_password@localhost:5432/boussole"
    
    # ============================================
    # Redis Settings
    # ============================================
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ============================================
    # Security Settings
    # ============================================
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # ============================================
    # CORS Settings
    # ============================================
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # ============================================
    # AI / LLM Settings
    # ============================================
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "groq"
    GROQ_MODEL: str = "mixtral-8x7b-32768"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # ============================================
    # RAG Settings
    # ============================================
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    VECTOR_SEARCH_TOP_K: int = 5
    VECTOR_SIMILARITY_THRESHOLD: float = 0.7
    
    # ============================================
    # Celery Settings
    # ============================================
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # ============================================
    # Data Ingestion Settings
    # ============================================
    DATA_SOURCES_ENABLED: List[str] = ["ons", "custom", "api"]
    RAW_DATA_PATH: str = "./data/raw"
    PROCESSED_DATA_PATH: str = "./data/processed"
    CACHE_PATH: str = "./data/cache"
    
    # ============================================
    # Logging Settings
    # ============================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # ============================================
    # Rate Limiting Settings
    # ============================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # ============================================
    # Email Settings (Optional)
    # ============================================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None
    SMTP_FROM_NAME: Optional[str] = None
    
    # ============================================
    # Monitoring Settings (Optional)
    # ============================================
    SENTRY_DSN: Optional[str] = None
    ANALYTICS_ENABLED: bool = False
    
    # ============================================
    # Feature Flags
    # ============================================
    FEATURE_RAG_ENABLED: bool = True
    FEATURE_MAPS_ENABLED: bool = True
    FEATURE_DASHBOARDS_ENABLED: bool = True
    FEATURE_EXPORT_ENABLED: bool = True
    FEATURE_API_ACCESS_ENABLED: bool = True
    FEATURE_MULTILINGUAL_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()


# Export settings instance
settings = get_settings()
