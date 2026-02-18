# ============================================
# Boussole - Metric Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class MetricBase(BaseModel):
    """Base Metric schema with common fields."""
    wilaya_id: int = Field(..., gt=0)
    sector_id: int = Field(..., gt=0)
    slug: str = Field(..., min_length=1, max_length=100)
    name_en: str = Field(..., min_length=1, max_length=200)
    name_fr: str = Field(..., min_length=1, max_length=200)
    name_ar: str = Field(..., min_length=1, max_length=200)
    value: float = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, max_length=50)
    period: str = Field(..., min_length=1, max_length=20)
    year: Optional[int] = None
    quarter: Optional[str] = Field(None, pattern="^Q[1-4]$")
    is_verified: bool = Field(default=False)
    is_featured: bool = Field(default=False)


class MetricCreate(MetricBase):
    """Schema for creating a new Metric."""
    code: Optional[str] = Field(None, max_length=50)
    description_en: Optional[str] = Field(None, max_length=500)
    description_fr: Optional[str] = Field(None, max_length=500)
    description_ar: Optional[str] = Field(None, max_length=500)
    source: Optional[str] = Field(None, max_length=200)


class MetricUpdate(BaseModel):
    """Schema for updating an existing Metric."""
    value: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=50)
    period: Optional[str] = Field(None, min_length=1, max_length=20)
    year: Optional[int] = None
    quarter: Optional[str] = Field(None, pattern="^Q[1-4]$")
    change_percent: Optional[float] = None
    change_value: Optional[float] = None
    trend: Optional[str] = Field(None, max_length=20)
    is_verified: Optional[bool] = None
    is_featured: Optional[bool] = None


class Metric(MetricBase):
    """Schema for Metric response."""
    id: int
    code: Optional[str] = None
    description_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    source: Optional[str] = None
    change_percent: Optional[float] = None
    change_value: Optional[float] = None
    trend: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MetricWithWilaya(Metric):
    """Schema for Metric with Wilaya details."""
    wilaya_code: str
    wilaya_name_en: str
    wilaya_name_fr: str
    wilaya_name_ar: str
    wilaya_region: Optional[str] = None


class MetricWithForecast(MetricWithWilaya):
    """Schema for Metric with forecast data."""
    forecasts: List[dict] = []


class DashboardKPI(BaseModel):
    """Schema for dashboard KPI card."""
    title: str
    value: float
    unit: Optional[str] = None
    change_percent: Optional[float] = None
    trend: Optional[str] = None
    period: str
    icon: Optional[str] = None
    color: Optional[str] = None


class WilayaHeatmapData(BaseModel):
    """Schema for Wilaya heatmap data."""
    wilaya_code: str
    wilaya_name_en: str
    wilaya_name_ar: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    value: float
    unit: Optional[str] = None
