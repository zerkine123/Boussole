# ============================================
# Boussole - Sector Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SectorBase(BaseModel):
    """Base sector schema with common fields."""
    slug: str = Field(..., min_length=1, max_length=100)
    name_en: str = Field(..., min_length=1, max_length=200)
    name_fr: str = Field(..., min_length=1, max_length=200)
    name_ar: str = Field(..., min_length=1, max_length=200)
    description_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_active: bool = True


class SectorCreate(SectorBase):
    """Schema for creating a new sector."""
    pass


class SectorUpdate(BaseModel):
    """Schema for updating an existing sector."""
    name_en: Optional[str] = Field(None, min_length=1, max_length=200)
    name_fr: Optional[str] = Field(None, min_length=1, max_length=200)
    name_ar: Optional[str] = Field(None, min_length=1, max_length=200)
    description_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    is_active: Optional[bool] = None


class Sector(SectorBase):
    """Schema for sector response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
