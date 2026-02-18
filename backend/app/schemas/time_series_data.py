# ============================================
# Boussole - TimeSeriesData Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class TimeSeriesDataBase(BaseModel):
    """Base TimeSeriesData schema with common fields."""
    sector_id: int = Field(..., gt=0)
    indicator_id: int = Field(..., gt=0)
    period: str = Field(..., min_length=1, max_length=20)
    value: float = Field(..., description="Data value")
    unit: Optional[str] = Field(None, max_length=50)
    is_verified: bool = Field(default=False)


class TimeSeriesDataCreate(TimeSeriesDataBase):
    """Schema for creating a new TimeSeriesData."""
    wilaya_id: Optional[int] = Field(None, gt=0)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    year: Optional[int] = None
    quarter: Optional[str] = Field(None, pattern="^Q[1-4]$")
    month: Optional[int] = Field(None, ge=1, le=12)
    source: Optional[str] = Field(None, max_length=200)
    source_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    meta_data: Optional[str] = None


class TimeSeriesDataUpdate(BaseModel):
    """Schema for updating an existing TimeSeriesData."""
    value: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=50)
    is_verified: Optional[bool] = None
    is_anomaly: Optional[bool] = None
    is_missing: Optional[bool] = None
    notes: Optional[str] = None
    meta_data: Optional[str] = None


class TimeSeriesData(TimeSeriesDataBase):
    """Schema for TimeSeriesData response."""
    id: int
    wilaya_id: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    year: Optional[int] = None
    quarter: Optional[str] = None
    month: Optional[int] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None
    meta_data: Optional[str] = None
    is_anomaly: bool = False
    is_missing: bool = False
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TimeSeriesDataWithDetails(TimeSeriesData):
    """Schema for TimeSeriesData with related details."""
    sector_name_en: Optional[str] = None
    sector_name_fr: Optional[str] = None
    sector_name_ar: Optional[str] = None
    indicator_name_en: Optional[str] = None
    indicator_name_fr: Optional[str] = None
    indicator_name_ar: Optional[str] = None
    indicator_unit: Optional[str] = None
    wilaya_name_en: Optional[str] = None
    wilaya_name_fr: Optional[str] = None
    wilaya_name_ar: Optional[str] = None
    wilaya_code: Optional[str] = None


class TimeSeriesBulkCreate(BaseModel):
    """Schema for bulk creating TimeSeriesData."""
    data_points: list[TimeSeriesDataCreate]


class TimeSeriesQuery(BaseModel):
    """Schema for querying TimeSeriesData."""
    sector_id: Optional[int] = None
    indicator_id: Optional[int] = None
    wilaya_id: Optional[int] = None
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    year: Optional[int] = None
    is_verified: Optional[bool] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
