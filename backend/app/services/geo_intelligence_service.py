# ============================================
# Boussole - Geographic Intelligence Service
# ============================================

"""
Core service for geographic intelligence.
Fetches data from Google Maps APIs (Places, Directions),
caches responses in Redis, and computes composite activity scores.
"""

import logging
import math
from typing import Any, Dict, List, Optional

import aiohttp

from app.core.config import settings
from app.schemas.geo import (
    AreaActivityScore,
    GeoIntelligenceResponse,
    LocationQuery,
    PlacePopularity,
    TrafficDensity,
)
from app.services.geo_cache_service import GeoCacheService

logger = logging.getLogger(__name__)

# Google Maps API base URLs
PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"


class GeoIntelligenceService:
    """
    Provides geographic intelligence by combining data from:
    - Google Places Nearby Search (business density & ratings)
    - Google Place Details (popularity signals)
    - Google Directions (live traffic conditions)

    All responses are cached in Redis with configurable TTL.
    """

    def __init__(self, cache: GeoCacheService):
        self.cache = cache
        self.api_key = settings.GOOGLE_MAPS_API_KEY or settings.GOOGLE_API_KEY
        if not self.api_key:
            logger.warning("No Google Maps API key configured — geo features disabled")

    def _is_available(self) -> bool:
        return bool(self.api_key)

    # ------------------------------------------------------------------
    # Google Places — Nearby Search
    # ------------------------------------------------------------------

    async def get_nearby_places(
        self,
        lat: float,
        lon: float,
        radius: int = 1000,
        place_type: Optional[str] = None,
    ) -> List[PlacePopularity]:
        """
        Fetch nearby places from Google Places API.
        Returns up to 20 results (Google's default page size).
        """
        if not self._is_available():
            return []

        cache_extra = f"{radius}:{place_type or 'all'}"
        cached = await self.cache.get("places", lat, lon, cache_extra)
        if cached:
            return [PlacePopularity(**p) for p in cached]

        params: Dict[str, Any] = {
            "location": f"{lat},{lon}",
            "radius": radius,
            "key": self.api_key,
        }
        if place_type:
            params["type"] = place_type

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(PLACES_NEARBY_URL, params=params) as resp:
                    data = await resp.json()

            if data.get("status") not in ("OK", "ZERO_RESULTS"):
                logger.error(f"Places API error: {data.get('status')} — {data.get('error_message', '')}")
                return []

            results = data.get("results", [])
            places = [
                PlacePopularity(
                    place_id=r["place_id"],
                    name=r.get("name", ""),
                    lat=r["geometry"]["location"]["lat"],
                    lon=r["geometry"]["location"]["lng"],
                    types=r.get("types", []),
                    rating=r.get("rating"),
                    user_ratings_total=r.get("user_ratings_total"),
                    price_level=r.get("price_level"),
                    vicinity=r.get("vicinity"),
                    business_status=r.get("business_status"),
                )
                for r in results
            ]

            # Cache the serialised list
            await self.cache.set(
                "places", lat, lon,
                [p.model_dump() for p in places],
                cache_extra,
            )

            return places

        except Exception as e:
            logger.error(f"Places API request failed: {e}")
            return []

    # ------------------------------------------------------------------
    # Google Directions — Traffic Density
    # ------------------------------------------------------------------

    async def get_traffic_density(
        self, lat: float, lon: float
    ) -> Optional[TrafficDensity]:
        """
        Estimate traffic congestion by comparing typical vs. live
        travel times for a short trip from the given location.
        Uses Google Directions API with departure_time=now.
        """
        if not self._is_available():
            return None

        cached = await self.cache.get("traffic", lat, lon)
        if cached:
            return TrafficDensity(**cached)

        # Create a short trip (~2 km north) to measure traffic
        dest_lat = lat + 0.018  # ~2 km north
        dest_lon = lon

        params = {
            "origin": f"{lat},{lon}",
            "destination": f"{dest_lat},{dest_lon}",
            "departure_time": "now",
            "key": self.api_key,
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(DIRECTIONS_URL, params=params) as resp:
                    data = await resp.json()

            if data.get("status") != "OK":
                logger.warning(f"Directions API: {data.get('status')}")
                return None

            leg = data["routes"][0]["legs"][0]
            typical_secs = leg["duration"]["value"]
            live_secs = leg.get("duration_in_traffic", {}).get("value", typical_secs)

            typical_min = typical_secs / 60
            live_min = live_secs / 60
            ratio = live_secs / max(typical_secs, 1)

            # Map ratio → 1-10 congestion
            congestion = min(10, max(1, round(ratio * 3.3)))

            descriptions = {
                (1, 3): "Light traffic — roads are clear",
                (4, 5): "Moderate traffic — some slowdowns",
                (6, 7): "Heavy traffic — significant delays",
                (8, 10): "Severe congestion — expect major delays",
            }
            desc = next(
                v for (lo, hi), v in descriptions.items() if lo <= congestion <= hi
            )

            traffic = TrafficDensity(
                congestion_level=congestion,
                typical_duration_minutes=round(typical_min, 1),
                live_duration_minutes=round(live_min, 1),
                traffic_ratio=round(ratio, 2),
                description=desc,
            )

            await self.cache.set("traffic", lat, lon, traffic.model_dump())
            return traffic

        except Exception as e:
            logger.error(f"Directions API request failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Composite Activity Score
    # ------------------------------------------------------------------

    async def compute_activity_score(
        self, lat: float, lon: float, radius: int = 1000
    ) -> AreaActivityScore:
        """
        Compute a 0–100 composite activity score for an area.

        Components (weighted):
          - Place density:   30 pts (based on place count in radius)
          - Avg rating:      20 pts (scaled from 0-5 → 0-20)
          - Review volume:   20 pts (log-scaled total reviews)
          - Type diversity:  15 pts (unique business categories)
          - Traffic:         15 pts (congestion level)
        """
        cached = await self.cache.get("score", lat, lon, str(radius))
        if cached:
            return AreaActivityScore(**cached)

        # Fetch data
        places = await self.get_nearby_places(lat, lon, radius)
        traffic = await self.get_traffic_density(lat, lon)

        place_count = len(places)

        # Avg rating
        rated = [p for p in places if p.rating is not None]
        avg_rating = sum(p.rating for p in rated) / len(rated) if rated else 0

        # Total reviews
        total_reviews = sum(p.user_ratings_total or 0 for p in places)

        # Type diversity
        all_types = set()
        for p in places:
            all_types.update(p.types)
        type_diversity = len(all_types)

        congestion = traffic.congestion_level if traffic else None

        # ---- Score calculation ----
        # Place density (0–30): 20 places → full score
        density_score = min(30, (place_count / 20) * 30)

        # Rating (0–20): 5.0 → full score
        rating_score = (avg_rating / 5.0) * 20 if avg_rating else 0

        # Review volume (0–20): log-scaled, 1000 reviews → full score
        review_score = min(20, (math.log10(max(total_reviews, 1)) / 3) * 20)

        # Type diversity (0–15): 15 unique types → full score
        diversity_score = min(15, type_diversity)

        # Traffic activity (0–15): higher congestion = more activity
        traffic_score = ((congestion or 3) / 10) * 15

        total = density_score + rating_score + review_score + diversity_score + traffic_score
        score = min(100, max(0, round(total)))

        # Label
        if score >= 80:
            label = "Very High"
        elif score >= 55:
            label = "High"
        elif score >= 30:
            label = "Moderate"
        else:
            label = "Low"

        result = AreaActivityScore(
            score=score,
            place_count=place_count,
            avg_rating=round(avg_rating, 2) if avg_rating else None,
            total_reviews=total_reviews,
            type_diversity=type_diversity,
            traffic_congestion=congestion,
            label=label,
        )

        await self.cache.set("score", lat, lon, result.model_dump(), str(radius))
        return result

    # ------------------------------------------------------------------
    # Full Intelligence Report
    # ------------------------------------------------------------------

    async def get_area_intelligence(
        self,
        lat: float,
        lon: float,
        radius: int = 1000,
        place_type: Optional[str] = None,
    ) -> GeoIntelligenceResponse:
        """
        Orchestrator: returns the full intelligence package.
        """
        # Check full-report cache
        cache_extra = f"full:{radius}:{place_type or 'all'}"
        cached = await self.cache.get("intelligence", lat, lon, cache_extra)
        if cached:
            return GeoIntelligenceResponse(**cached, cached=True)

        places = await self.get_nearby_places(lat, lon, radius, place_type)
        traffic = await self.get_traffic_density(lat, lon)
        activity = await self.compute_activity_score(lat, lon, radius)

        location = LocationQuery(lat=lat, lon=lon, radius=radius)

        response = GeoIntelligenceResponse(
            location=location,
            activity_score=activity,
            traffic=traffic,
            nearby_places=places,
            cached=False,
        )

        # Cache the full report
        await self.cache.set(
            "intelligence", lat, lon,
            response.model_dump(exclude={"cached"}),
            cache_extra,
        )

        return response
