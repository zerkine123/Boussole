# ============================================
# Boussole - Sector Model
# ============================================

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Sector(Base):
    """
    Sector model for organizing data by economic/social sectors.
    """
    
    __tablename__ = "sectors"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name_en = Column(String(200), nullable=False)
    name_fr = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=False)
    description_en = Column(Text)
    description_fr = Column(Text)
    description_ar = Column(Text)
    icon = Column(String(50))  # Icon identifier (e.g., "leaf", "zap", "factory")
    color = Column(String(7))  # Hex color code (e.g., "#22c55e")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    indicators = relationship("Indicator", back_populates="sector", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="sector", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Sector(id={self.id}, slug={self.slug}, name_en={self.name_en})>"
