# ============================================
# Boussole - Metric Model
# ============================================

"""
Metric model for storing aggregated metrics by Wilaya and sector.
Metrics are pre-calculated KPIs for dashboard display.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Metric(Base):
    """
    Metric model for storing KPIs and aggregated data.
    """
    
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    wilaya_id = Column(Integer, ForeignKey("wilayas.id", ondelete="CASCADE"), nullable=False, index=True)
    sector_id = Column(Integer, ForeignKey("sectors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Metric identification
    slug = Column(String(100), index=True, nullable=False)
    code = Column(String(50))  # Official metric code
    name_en = Column(String(200), nullable=False)
    name_fr = Column(String(200), nullable=False)
    name_ar = Column(String(200), nullable=False)
    description_en = Column(String(500))
    description_fr = Column(String(500))
    description_ar = Column(String(500))
    
    # Metric values
    value = Column(Float, nullable=False)
    unit = Column(String(50))  # Unit of measurement
    period = Column(String(20), index=True)  # e.g., "2024", "2024-Q1"
    year = Column(Integer, index=True)
    quarter = Column(String(5))  # Q1, Q2, Q3, Q4
    
    # Change tracking
    change_percent = Column(Float)  # Year-over-year change percentage
    change_value = Column(Float)  # Year-over-year change value
    trend = Column(String(20))  # up, down, stable
    
    # Metadata
    source = Column(String(200))  # Data source
    is_verified = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)  # Highlight on dashboard
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wilaya = relationship("Wilaya", back_populates="metrics")
    sector = relationship("Sector", back_populates="metrics")
    forecasts = relationship("Forecast", back_populates="metric", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Metric(id={self.id}, slug={self.slug}, value={self.value})>"
