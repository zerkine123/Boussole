# ============================================
# Boussole - Business Intent Schema
# ============================================

"""
Structured intent schema for AI-parsed business queries.
This is the universal output consumed by the Widget Registry,
Data Service, and Layout Generator.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class GeographicScope(str, Enum):
    NATIONAL = "national"
    REGIONAL = "regional"
    LOCAL = "local"


class BusinessObjective(str, Enum):
    MARKET_ANALYSIS = "market_analysis"
    FEASIBILITY = "feasibility"
    COMPETITION = "competition"
    INVESTMENT = "investment"
    TREND_TRACKING = "trend_tracking"
    COMPARISON = "comparison"
    GENERAL = "general"


class DataCategory(str, Enum):
    MARKET_DEMAND = "market_demand"
    COMPETITION = "competition"
    FINANCE = "finance"
    INFRASTRUCTURE = "infrastructure"
    DEMOGRAPHICS = "demographics"
    LABOR = "labor"
    REGULATION = "regulation"
    TRADE = "trade"


# ---- Request / Response ----

class IntentParseRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000, description="User business query")
    context: Optional[str] = Field(None, description="Optional context from previous interactions")


class BusinessIntent(BaseModel):
    """
    Rich, structured representation of a user's business query.
    This is the foundation for widget selection and data activation.
    """

    # Core classification
    sector: str = Field(..., description="Business sector: agriculture, energy, manufacturing, services, tourism, etc.")
    subsector: Optional[str] = Field(None, description="Specific subsector: greenhouses, solar_panels, bakeries, etc.")

    # Geographic scope
    location: Optional[str] = Field(None, description="Wilaya code 01-58, or None for national")
    location_name: Optional[str] = Field(None, description="Human-readable location name")
    geographic_scope: GeographicScope = Field(default=GeographicScope.NATIONAL)

    # Business objective
    objective: BusinessObjective = Field(default=BusinessObjective.GENERAL)

    # Required data categories
    data_categories: list[DataCategory] = Field(
        default_factory=lambda: [DataCategory.MARKET_DEMAND],
        description="What types of data the user needs"
    )

    # Metadata
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    raw_query: str = Field(default="")

    # Time scope
    time_range: Optional[str] = Field(None, description="last_year, 5_years, current, etc.")


class IntentParseResponse(BaseModel):
    """API response wrapping the parsed intent."""
    intent: BusinessIntent
    provider: str = Field(..., description="LLM provider used for parsing")
    model: str = Field(..., description="Model used for parsing")
