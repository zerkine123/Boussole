# ============================================
# Boussole - Wilaya Model
# ============================================

"""
Wilaya model for Algerian provinces (departments).
Wilaya is the Arabic term for Algeria's 58 provinces.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Wilaya(Base):
    """
    Wilaya (province) model for Algerian administrative divisions.
    """
    
    __tablename__ = "wilayas"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)  # Wilaya code (01-58)
    name_en = Column(String(100), nullable=False)
    name_fr = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=False)
    name_arabic = Column(String(100), nullable=False)  # Arabic name in Arabic script
    
    # Geographic data for PostGIS
    latitude = Column(Float)
    longitude = Column(Float)
    area_km2 = Column(Float)  # Area in square kilometers
    population = Column(Integer)  # Population (optional, from census)
    
    # Regional grouping
    region = Column(String(50))  # North, South, East, West, Central
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    metrics = relationship("Metric", back_populates="wilaya", cascade="all, delete-orphan")
    time_series_data = relationship("TimeSeriesData", back_populates="wilaya", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Wilaya(code={self.code}, name_en={self.name_en})>"
