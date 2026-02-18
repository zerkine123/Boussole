# ============================================
# Boussole - Wilaya Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class WilayaBase(BaseModel):
    """Base Wilaya schema with common fields."""
    code: str = Field(..., min_length=2, max_length=10, description="Wilaya code (01-58)")
    name_en: str = Field(..., min_length=1, max_length=100)
    name_fr: str = Field(..., min_length=1, max_length=100)
    name_ar: str = Field(..., min_length=1, max_length=100)
    name_arabic: str = Field(..., min_length=1, max_length=100)
    region: Optional[str] = Field(None, max_length=50)
    is_active: bool = Field(default=True)


class WilayaCreate(WilayaBase):
    """Schema for creating a new Wilaya."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_km2: Optional[float] = None
    population: Optional[int] = None


class WilayaUpdate(BaseModel):
    """Schema for updating an existing Wilaya."""
    name_en: Optional[str] = Field(None, min_length=1, max_length=100)
    name_fr: Optional[str] = Field(None, min_length=1, max_length=100)
    name_ar: Optional[str] = Field(None, min_length=1, max_length=100)
    name_arabic: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_km2: Optional[float] = None
    population: Optional[int] = None
    region: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class Wilaya(WilayaBase):
    """Schema for Wilaya response."""
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area_km2: Optional[float] = None
    population: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WilayaList(BaseModel):
    """Schema for list of Wilayas with metrics."""
    id: int
    code: str
    name_en: str
    name_fr: str
    name_ar: str
    region: Optional[str] = None
    metrics_count: int = 0
