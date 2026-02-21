# ============================================
# Boussole - Insight Model
# ============================================

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Insight(Base):
    """
    Insight model for storing AI-generated or system-generated insights.
    """
    
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    sector_id = Column(Integer, ForeignKey("sectors.id", ondelete="CASCADE"), nullable=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=True, index=True)
    
    type = Column(String(50), nullable=False)  # trend, anomaly, summary, correlation
    title_en = Column(String(300), nullable=False)
    title_fr = Column(String(300), nullable=False)
    title_ar = Column(String(300), nullable=False)
    content_en = Column(Text, nullable=False)
    content_fr = Column(Text, nullable=False)
    content_ar = Column(Text, nullable=False)
    
    importance_score = Column(Float, default=0.0)  # 0.0 to 10.0
    period = Column(String(50))  # E.g. "2024-Q1", "2024"
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sector = relationship("Sector")
    indicator = relationship("Indicator")
    
    def __repr__(self):
        return f"<Insight(id={self.id}, type={self.type}, title_en={self.title_en})>"
