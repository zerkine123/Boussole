# ============================================
# Boussole - Indicator Model
# ============================================

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Indicator(Base):
    """
    Indicator model for tracking specific metrics within sectors.
    """
    
    __tablename__ = "indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    sector_id = Column(Integer, ForeignKey("sectors.id", ondelete="CASCADE"), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    code = Column(String(50))  # Official indicator code (e.g., from ONS)
    name_en = Column(String(300), nullable=False)
    name_fr = Column(String(300), nullable=False)
    name_ar = Column(String(300), nullable=False)
    description_en = Column(Text)
    description_fr = Column(Text)
    description_ar = Column(Text)
    unit = Column(String(50))  # Unit of measurement (e.g., "%", "millions DZD", "tons")
    frequency = Column(String(20))  # Data frequency: monthly, quarterly, annually
    source = Column(String(200))  # Data source (e.g., "ONS", "Ministry of Energy")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sector = relationship("Sector", back_populates="indicators")
    data_points = relationship("DataPoint", back_populates="indicator", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Indicator(id={self.id}, slug={self.slug}, name_en={self.name_en})>"
