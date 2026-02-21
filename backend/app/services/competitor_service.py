# ============================================
# Boussole - Competitor Intelligence Service
# ============================================

"""
Orchestrates competitor data retrieval and market saturation analysis.
Uses GeoIntelligenceService to fetch raw place data and computes
density/saturation metrics for specific business categories.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.geo_intelligence_service import GeoIntelligenceService
from app.schemas.geo import PlacePopularity

logger = logging.getLogger(__name__)

class CompetitorMappingService:
    def __init__(self, db: AsyncSession, geo_service: GeoIntelligenceService):
        self.db = db
        self.geo_service = geo_service

    async def get_competitors(
        self, 
        latitude: float, 
        longitude: float, 
        sector: str,
        radius: int = 2000
    ) -> Dict[str, Any]:
        """
        Fetch competitors for a given sector and location.
        Returns a list of places and a saturation index.
        """
        if not self.geo_service:
            logger.warning("GeoService not available for competitor mapping")
            return {"competitors": [], "saturation_index": 0, "label": "Unknown"}

        # Map sector to Google Places types
        # This expands on the basic mapping in DemandService
        type_map = {
            "agriculture": "farm",
            "manufacturing": "factory", # Rare in Places API, maybe 'establishment'
            "services": ["consulting", "agency", "finance", "lawyer"],
            "technology": ["software", "electronics_store", "computer_store"],
            "tourism": ["hotel", "travel_agency", "museum"],
            "energy": "gas_station", # Poor proxy, but best available
            "construction": ["general_contractor", "hardware_store"],
            "commerce": ["store", "shopping_mall", "supermarket"],
            "health": ["doctor", "hospital", "pharmacy", "dentist"],
            "education": ["school", "university", "library"],
            "transport": ["moving_company", "taxi_stand", "bus_station"],
            "housing": "real_estate_agency",
            "coffee": ["cafe", "bakery"],
            "restaurant": ["restaurant", "meal_takeaway"],
        }

        # Determine place types to search
        search_types = type_map.get(sector.lower(), "establishment")
        if isinstance(search_types, str):
            search_types = [search_types]

        all_places: List[PlacePopularity] = []
        
        # Search for each type (Google API limits to one type per request usually, 
        # but GeoService might handle it. We'll iterate to be safe if needed, 
        # but GeoService takes a single string. We'll join or loop.)
        # GeoService.get_nearby_places takes `place_type: str`.
        
        for p_type in search_types:
            try:
                places = await self.geo_service.get_nearby_places(
                    latitude, longitude, radius, p_type
                )
                all_places.extend(places)
            except Exception as e:
                logger.error(f"Error fetching competitors for {p_type}: {e}")

        # Deduplicate by place_id
        unique_places = {p.place_id: p for p in all_places}.values()
        competitors = list(unique_places)

        # Compute Saturation Index (0-100)
        # Simple heuristic: 
        # Low saturation (<5 places): Opportunity
        # Moderate (5-15): Healthy
        # High (>20): Saturated
        
        count = len(competitors)
        if count <= 5:
            sat_index = count * 10 # 0-50
            label = "Low Saturation (High Opportunity)"
        elif count <= 15:
            sat_index = 50 + (count - 5) * 3 # 50-80
            label = "Moderate Competition"
        else:
            sat_index = min(100, 80 + (count - 15) * 2) # 80-100
            label = "High Saturation"

        return {
            "competitors": [p.model_dump() for p in competitors],
            "saturation_index": sat_index,
            "saturation_label": label,
            "total_count": count
        }
