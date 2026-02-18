# ============================================
# Boussole - TimeSeriesData Model
# ============================================

"""
TimeSeriesData model for storing time-series data points.
This is the raw data that feeds into metrics and forecasts.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class TimeSeriesData(Base):
    """
    TimeSeriesData model for storing raw time-series data.
    """
    
    __tablename__ = "time_series_data"
    
    id = Column(Integer, primary_key=True, index=True)
    wilaya_id = Column(Integer, ForeignKey("wilayas.id", ondelete="SET NULL"), index=True)
    sector_id = Column(Integer, ForeignKey("sectors.id", ondelete="CASCADE"), nullable=False, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Time period
    period = Column(String(20), index=True, nullable=False)  # e.g., "2024-01", "2024-Q1"
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    year = Column(Integer, index=True)
    quarter = Column(String(5))  # Q1, Q2, Q3, Q4
    month = Column(Integer)  # 1-12
    
    # Data values
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    
    # Quality and metadata
    is_verified = Column(Boolean, default=False)
    source = Column(String(200))
    source_url = Column(String(500))
    notes = Column(Text)
    meta_data = Column(Text)  # Additional metadata as JSON
    
    # Flags
    is_anomaly = Column(Boolean, default=False)  # Flagged as anomaly
    is_missing = Column(Boolean, default=False)  # Flagged as missing/estimated
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wilaya = relationship("Wilaya")
    sector = relationship("Sector")
    indicator = relationship("Indicator")
    
    def __repr__(self):
        return f"<TimeSeriesData(id={self.id}, period={self.period}, value={self.value})>"
