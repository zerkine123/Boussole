# ============================================
# Boussole - Intent Management Models
# ============================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON, Text, Index
from datetime import datetime
from app.db.base import Base


class IntentLog(Base):
    """
    Audit log for all LLM-parsed business queries.
    Used by admins to monitor accuracy and performance.
    """
    __tablename__ = "intent_logs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(1000), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # groq, openai, fallback
    model_name = Column(String(100), nullable=False)
    
    # Execution metrics
    latency_ms = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Store the actual raw Intent parse
    parsed_intent = Column(JSON, nullable=False)
    
    # Admin auditing flags
    is_accurate = Column(Boolean, nullable=True)  # True/False marked by admin
    feedback_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<IntentLog(id={self.id}, query='{self.query[:30]}...', provider={self.provider})>"


class StaticIntent(Base):
    """
    Exact keyword mappings to bypass the LLM for popular routing cases.
    E.g. "bakery" -> pre-configured JSON.
    """
    __tablename__ = "static_intents"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), unique=True, index=True, nullable=False)
    
    # The exact BusinessIntent JSON structure returned
    mapped_intent = Column(JSON, nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<StaticIntent(keyword='{self.keyword}', active={self.is_active})>"


class SystemPrompt(Base):
    """
    Table to store and version the core Intent System Prompt.
    Allows admins to tweak instructions without redeploying.
    """
    __tablename__ = "system_prompts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)  # "intent_parser", "summary_bot"
    content = Column(Text, nullable=False)
    description = Column(String(500), nullable=True)
    
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    
    updated_by = Column(Integer, nullable=True) # User ID tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemPrompt(name='{self.name}', version={self.version}, active={self.is_active})>"
