# ============================================
# Boussole - Data Point Model
# ============================================

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class DataPoint(Base):
    """
    DataPoint model for storing actual data values for indicators.
    """
    
    __tablename__ = "data_points"
    
    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False)
    value = Column(Float, nullable=False)
    period = Column(String(20), nullable=False)  # Time period (e.g., "2024-Q1", "2024-01")
    period_start = Column(DateTime)  # Start date of the period
    period_end = Column(DateTime)  # End date of the period
    region = Column(String(100))  # Geographic region (e.g., "Algiers", "Oran", "National")
    region_code = Column(String(10))  # Region code (e.g., "01", "16")
    meta_data = Column(Text)  # Additional metadata as JSON
    is_verified = Column(Boolean, default=False)
    source_url = Column(String(500))  # URL to source data
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    indicator = relationship("Indicator", back_populates="data_points")
    
    def __repr__(self):
        return f"<DataPoint(id={self.id}, indicator_id={self.indicator_id}, value={self.value}, period={self.period})>"
