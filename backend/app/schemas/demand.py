# ============================================
# Boussole - Market Demand Intelligence Schemas
# ============================================

"""
Pydantic models for demand analysis, opportunity scoring,
and market feasibility reports.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class DemandSignal(BaseModel):
    """One component of the demand score breakdown."""
    name: str = Field(..., description="Signal name")
    score: float = Field(..., description="Signal score 0-100", ge=0, le=100)
    weight: float = Field(..., description="Weight in composite (0-1)")
    weighted_score: float = Field(..., description="score * weight")
    detail: str = Field("", description="Human-readable explanation")


class DemandScore(BaseModel):
    """Composite demand/opportunity score for a sector in a location."""
    sector: str
    wilaya_code: Optional[str] = None
    wilaya_name: Optional[str] = None
    score: int = Field(..., description="Composite demand score 0-100", ge=0, le=100)
    label: str = Field("", description="Low / Moderate / High / Very High")
    recommendation: str = Field("", description="One-line recommendation")
    signals: List[DemandSignal] = []


class SectorOpportunity(BaseModel):
    """A ranked sector opportunity for a given location."""
    rank: int
    sector: str
    sector_name: str
    score: int = Field(..., ge=0, le=100)
    label: str
    key_signals: List[str] = Field([], description="Top 2-3 signal summaries")


class FeasibilityReport(BaseModel):
    """Full feasibility report combining demand, geo, and competitive analysis."""
    sector: str
    wilaya_code: Optional[str] = None
    wilaya_name: Optional[str] = None
    demand_score: DemandScore
    activity_score: Optional[int] = Field(None, description="Geo activity 0-100")
    competition_count: Optional[int] = Field(None, description="Nearby competitors")
    avg_competitor_rating: Optional[float] = None
    verdict: str = Field("", description="Feasible / Risky / Not Recommended / Highly Favorable")
    summary: str = Field("", description="2-3 sentence feasibility summary")
