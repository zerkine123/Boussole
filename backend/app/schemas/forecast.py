# ============================================
# Boussole - Forecast Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class ForecastBase(BaseModel):
    """Base Forecast schema with common fields."""
    metric_id: int = Field(..., gt=0)
    forecast_period: str = Field(..., min_length=1, max_length=20)
    forecast_value: float = Field(..., description="Forecasted value")
    confidence_interval: float = Field(default=0.95, ge=0.5, le=1.0)


class ForecastCreate(ForecastBase):
    """Schema for creating a new Forecast."""
    wilaya_id: Optional[int] = Field(None, gt=0)
    year: Optional[int] = None
    quarter: Optional[str] = Field(None, pattern="^Q[1-4]$")
    month: Optional[int] = Field(None, ge=1, le=12)
    forecast_horizon: int = Field(default=1, ge=1, le=36)
    model_version: Optional[str] = Field(None, max_length=50)
    model_params: Optional[str] = None
    notes: Optional[str] = None
    is_published: bool = Field(default=False)


class Forecast(ForecastBase):
    """Schema for Forecast response."""
    id: int
    wilaya_id: Optional[int] = None
    year: Optional[int] = None
    quarter: Optional[str] = None
    month: Optional[int] = None
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    forecast_horizon: Optional[int] = None
    model_version: Optional[str] = None
    model_params: Optional[str] = None
    mae: Optional[float] = None
    mape: Optional[float] = None
    rmse: Optional[float] = None
    notes: Optional[str] = None
    is_published: bool = False
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ForecastWithMetric(Forecast):
    """Schema for Forecast with metric details."""
    metric_name_en: Optional[str] = None
    metric_name_fr: Optional[str] = None
    metric_name_ar: Optional[str] = None
    metric_unit: Optional[str] = None
    metric_period: Optional[str] = None
    metric_value: Optional[float] = None


class ForecastGenerateRequest(BaseModel):
    """Schema for generating forecasts."""
    metric_id: int = Field(..., gt=0)
    periods: int = Field(default=12, ge=1, le=36, description="Number of periods to forecast")
    confidence_interval: float = Field(default=0.95, ge=0.5, le=1.0)


class ForecastGenerateResponse(BaseModel):
    """Schema for forecast generation response."""
    metric_id: int
    forecasts: List[Forecast] = []
    model_version: str
    mae: Optional[float] = None
    mape: Optional[float] = None
    rmse: Optional[float] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ForecastTrend(BaseModel):
    """Schema for forecast trend visualization."""
    period: str
    actual_value: Optional[float] = None
    forecast_value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
