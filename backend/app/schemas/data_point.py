# ============================================
# Boussole - Data Point Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class DataPointBase(BaseModel):
    """Base data point schema with common fields."""
    indicator_id: int = Field(..., gt=0)
    value: float = Field(..., description="The numeric value of the data point")
    period: str = Field(..., min_length=1, max_length=20, description="Time period (e.g., '2024-Q1', '2024-01')")
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    region: Optional[str] = Field(None, max_length=100, description="Geographic region")
    region_code: Optional[str] = Field(None, max_length=10, description="Region code")
    metadata: Optional[str] = None
    source_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    is_verified: bool = False


class DataPointCreate(DataPointBase):
    """Schema for creating a new data point."""
    pass


class DataPointUpdate(BaseModel):
    """Schema for updating an existing data point."""
    value: Optional[float] = None
    period: Optional[str] = Field(None, min_length=1, max_length=20)
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    region: Optional[str] = Field(None, max_length=100)
    region_code: Optional[str] = Field(None, max_length=10)
    metadata: Optional[str] = None
    source_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    is_verified: Optional[bool] = None


class DataPoint(DataPointBase):
    """Schema for data point response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DataPointBulkCreate(BaseModel):
    """Schema for bulk creating data points."""
    data_points: list[DataPointCreate]


class DataPointQuery(BaseModel):
    """Schema for querying data points."""
    indicator_id: Optional[int] = None
    sector_id: Optional[int] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    region: Optional[str] = None
    is_verified: Optional[bool] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
