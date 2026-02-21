# ============================================
# Boussole - Geographic Intelligence Schemas
# ============================================

"""
Pydantic models for geographic intelligence endpoints.
Covers location queries, traffic density, place popularity,
and composite area activity scores.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class PlaceType(str, Enum):
    """Common Google Places types relevant to business analysis."""
    restaurant = "restaurant"
    cafe = "cafe"
    store = "store"
    supermarket = "supermarket"
    bank = "bank"
    pharmacy = "pharmacy"
    hospital = "hospital"
    school = "school"
    gas_station = "gas_station"
    shopping_mall = "shopping_mall"
    bakery = "bakery"
    hotel = "hotel"
    gym = "gym"
    parking = "parking"


# ------------------------------------------------------------------
# Request models
# ------------------------------------------------------------------

class LocationQuery(BaseModel):
    """Query parameters for geographic intelligence."""
    lat: float = Field(..., description="Latitude", ge=-90, le=90)
    lon: float = Field(..., description="Longitude", ge=-180, le=180)
    radius: int = Field(1000, description="Search radius in meters", ge=100, le=50000)
    place_type: Optional[PlaceType] = Field(None, description="Filter by place type")


class WilayaGeoQuery(BaseModel):
    """Query geographic intelligence by wilaya code."""
    wilaya_code: str = Field(..., description="Wilaya code (01-58)")
    radius: int = Field(2000, description="Search radius in meters", ge=100, le=50000)
    place_type: Optional[PlaceType] = Field(None, description="Filter by place type")


# ------------------------------------------------------------------
# Response models
# ------------------------------------------------------------------

class TrafficDensity(BaseModel):
    """Traffic congestion information for a location."""
    congestion_level: int = Field(..., description="Congestion 1-10 (10 = severe)", ge=1, le=10)
    typical_duration_minutes: Optional[float] = Field(None, description="Typical travel time (no traffic)")
    live_duration_minutes: Optional[float] = Field(None, description="Current travel time (with traffic)")
    traffic_ratio: Optional[float] = Field(None, description="Live / typical ratio (>1 = congested)")
    description: str = Field("", description="Human-readable congestion description")


class PlacePopularity(BaseModel):
    """Popularity data for a nearby place."""
    place_id: str
    name: str
    lat: float
    lon: float
    types: List[str] = []
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    price_level: Optional[int] = Field(None, description="0-4 price level")
    vicinity: Optional[str] = None
    business_status: Optional[str] = None


class AreaActivityScore(BaseModel):
    """
    Composite activity score for an area.
    Combines place density, ratings, diversity, and traffic.
    """
    score: int = Field(..., description="Activity score 0-100", ge=0, le=100)
    place_count: int = Field(0, description="Number of places in radius")
    avg_rating: Optional[float] = Field(None, description="Average place rating")
    total_reviews: int = Field(0, description="Sum of all reviews in area")
    type_diversity: int = Field(0, description="Number of unique place types")
    traffic_congestion: Optional[int] = Field(None, description="Congestion level 1-10")
    label: str = Field("", description="Human label: Low / Moderate / High / Very High")


class GeoIntelligenceResponse(BaseModel):
    """Full geographic intelligence response for a location."""
    location: LocationQuery
    activity_score: AreaActivityScore
    traffic: Optional[TrafficDensity] = None
    nearby_places: List[PlacePopularity] = []
    cached: bool = Field(False, description="Whether this response was served from cache")
