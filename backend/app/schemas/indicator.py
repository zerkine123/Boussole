# ============================================
# Boussole - Indicator Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class IndicatorBase(BaseModel):
    """Base indicator schema with common fields."""
    sector_id: int = Field(..., gt=0)
    slug: str = Field(..., min_length=1, max_length=100)
    code: Optional[str] = Field(None, max_length=50)
    name_en: str = Field(..., min_length=1, max_length=300)
    name_fr: str = Field(..., min_length=1, max_length=300)
    name_ar: str = Field(..., min_length=1, max_length=300)
    description_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=50)
    frequency: Optional[str] = Field(None, pattern="^(monthly|quarterly|annually|weekly|daily)$")
    source: Optional[str] = Field(None, max_length=200)
    is_active: bool = True


class IndicatorCreate(IndicatorBase):
    """Schema for creating a new indicator."""
    pass


class IndicatorUpdate(BaseModel):
    """Schema for updating an existing indicator."""
    sector_id: Optional[int] = Field(None, gt=0)
    name_en: Optional[str] = Field(None, min_length=1, max_length=300)
    name_fr: Optional[str] = Field(None, min_length=1, max_length=300)
    name_ar: Optional[str] = Field(None, min_length=1, max_length=300)
    description_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=50)
    frequency: Optional[str] = Field(None, pattern="^(monthly|quarterly|annually|weekly|daily)$")
    source: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None


class Indicator(IndicatorBase):
    """Schema for indicator response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
