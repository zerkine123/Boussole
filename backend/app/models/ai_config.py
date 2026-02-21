from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base

class AIProviderConfig(Base):
    __tablename__ = "ai_provider_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_name: Mapped[str] = mapped_column(String, unique=True, index=True) # "groq", "openai", "azure", "gemini", "anthropic"
    api_key: Mapped[str] = mapped_column(String) # Ensure encryption in a true prod environment, but fine here
    api_base_url: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Used for Azure endpoints
    model_name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
