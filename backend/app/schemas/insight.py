# ============================================
# Boussole - Insight Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class InsightBase(BaseModel):
    """Base Insight schema with common fields."""
    sector_id: Optional[int] = Field(None, gt=0)
    indicator_id: Optional[int] = Field(None, gt=0)
    
    type: str = Field(..., max_length=50, description="Type of insight: trend, anomaly, summary, correlation")
    title_en: str = Field(..., max_length=300)
    title_fr: str = Field(..., max_length=300)
    title_ar: str = Field(..., max_length=300)
    content_en: str
    content_fr: str
    content_ar: str
    
    importance_score: float = Field(0.0, ge=0.0, le=10.0, description="Importance score from 0.0 to 10.0")
    period: Optional[str] = Field(None, max_length=50)
    is_active: bool = Field(default=True)


class InsightCreate(InsightBase):
    """Schema for creating a new Insight."""
    pass


class InsightUpdate(BaseModel):
    """Schema for updating an existing Insight."""
    sector_id: Optional[int] = None
    indicator_id: Optional[int] = None
    type: Optional[str] = Field(None, max_length=50)
    title_en: Optional[str] = Field(None, max_length=300)
    title_fr: Optional[str] = Field(None, max_length=300)
    title_ar: Optional[str] = Field(None, max_length=300)
    content_en: Optional[str] = None
    content_fr: Optional[str] = None
    content_ar: Optional[str] = None
    importance_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    period: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class InsightResponse(InsightBase):
    """Schema for Insight response, including DB fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class InsightWithDetailsResponse(InsightResponse):
    """Schema for Insight with related sector and indicator names."""
    sector_name_en: Optional[str] = None
    sector_name_fr: Optional[str] = None
    sector_name_ar: Optional[str] = None
    
    indicator_name_en: Optional[str] = None
    indicator_name_fr: Optional[str] = None
    indicator_name_ar: Optional[str] = None
    indicator_unit: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class InsightQuery(BaseModel):
    """Schema for querying Insights."""
    sector_id: Optional[int] = None
    indicator_id: Optional[int] = None
    type: Optional[str] = None
    period: Optional[str] = None
    is_active: Optional[bool] = None
    min_importance: Optional[float] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=100)
