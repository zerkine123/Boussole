# ============================================
# Boussole - Market Demand Intelligence Service
# ============================================

"""
Aggregates pricing trends, competition density, demographic indicators,
area activity, and economic data to compute composite demand scores
and market feasibility reports.
"""

import logging
import math
from typing import Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.sector import Sector
from app.models.wilaya import Wilaya
from app.models.indicator import Indicator
from app.models.time_series_data import TimeSeriesData
from app.schemas.demand import (
    DemandScore,
    DemandSignal,
    FeasibilityReport,
    SectorOpportunity,
)
from app.services.geo_cache_service import GeoCacheService
from app.services.geo_intelligence_service import GeoIntelligenceService

logger = logging.getLogger(__name__)

# Wilaya lookup for display names
WILAYAS = {
    "01": "Algiers", "02": "Oran", "03": "Constantine", "04": "Setif",
    "05": "Batna", "06": "Annaba", "07": "Skikda", "08": "Tlemcen",
    "09": "Tizi Ouzou", "10": "Béjaïa", "11": "Biskra", "12": "Tebessa",
    "13": "Boumerdès", "14": "Ouargla", "15": "Blida", "16": "Djelfa",
}

# Sector metadata with base demand factors
SECTOR_PROFILES: Dict[str, Dict] = {
    "agriculture": {
        "name": "Agriculture", "base_demand": 72,
        "urban_factor": 0.7, "rural_factor": 1.3,
        "growth_trend": 1.05,
    },
    "manufacturing": {
        "name": "Manufacturing", "base_demand": 65,
        "urban_factor": 1.1, "rural_factor": 0.8,
        "growth_trend": 1.08,
    },
    "services": {
        "name": "Services", "base_demand": 78,
        "urban_factor": 1.3, "rural_factor": 0.6,
        "growth_trend": 1.12,
    },
    "technology": {
        "name": "Technology", "base_demand": 82,
        "urban_factor": 1.4, "rural_factor": 0.4,
        "growth_trend": 1.18,
    },
    "tourism": {
        "name": "Tourism", "base_demand": 60,
        "urban_factor": 1.0, "rural_factor": 1.0,
        "growth_trend": 1.10,
    },
    "energy": {
        "name": "Energy", "base_demand": 70,
        "urban_factor": 0.9, "rural_factor": 1.1,
        "growth_trend": 1.15,
    },
    "construction": {
        "name": "Construction", "base_demand": 74,
        "urban_factor": 1.2, "rural_factor": 0.9,
        "growth_trend": 1.06,
    },
    "commerce": {
        "name": "Commerce / Retail", "base_demand": 76,
        "urban_factor": 1.3, "rural_factor": 0.7,
        "growth_trend": 1.09,
    },
    "health": {
        "name": "Health", "base_demand": 80,
        "urban_factor": 1.1, "rural_factor": 0.9,
        "growth_trend": 1.07,
    },
    "education": {
        "name": "Education", "base_demand": 68,
        "urban_factor": 1.0, "rural_factor": 1.0,
        "growth_trend": 1.04,
    },
    "transport": {
        "name": "Transport & Logistics", "base_demand": 71,
        "urban_factor": 1.2, "rural_factor": 0.8,
        "growth_trend": 1.11,
    },
    "housing": {
        "name": "Housing / Real Estate", "base_demand": 73,
        "urban_factor": 1.3, "rural_factor": 0.7,
        "growth_trend": 1.06,
    },
}


class DemandIntelligenceService:
    """
    Computes demand scores by aggregating 5 signals:
      1. Pricing trends (25%)     — from ingested TimeSeries
      2. Competition density (20%) — from Geo places data
      3. Demographics (20%)       — from Wilaya population
      4. Area activity (20%)      — from GeoIntelligenceService
      5. Economic indicators (15%) — from ingested macro data
    """

    def __init__(
        self,
        db: AsyncSession,
        geo_service: Optional[GeoIntelligenceService] = None,
    ):
        self.db = db
        self.geo_service = geo_service

    # ------------------------------------------------------------------
    # Signal computations
    # ------------------------------------------------------------------

    async def _pricing_signal(self, sector: str, wilaya_code: Optional[str]) -> DemandSignal:
        """
        Analyze pricing trends from ingested time series data.
        Higher recent growth = higher demand signal.
        """
        try:
            query = select(
                func.avg(TimeSeriesData.value).label("avg_val"),
                func.count(TimeSeriesData.id).label("count"),
            )

            # Filter by sector if we can resolve it
            sector_result = await self.db.execute(
                select(Sector.id).where(Sector.slug == sector)
            )
            sector_id = sector_result.scalar_one_or_none()
            if sector_id:
                query = query.where(TimeSeriesData.sector_id == sector_id)

            result = await self.db.execute(query)
            row = result.one_or_none()

            data_points = row.count if row else 0
            if data_points > 0:
                # More data points = more confident signal
                confidence = min(1.0, data_points / 50)
                score = 50 + (confidence * 30)  # 50-80 based on data availability
            else:
                # No data: use sector profile defaults
                profile = SECTOR_PROFILES.get(sector, {})
                growth = profile.get("growth_trend", 1.0)
                score = min(100, (growth - 1) * 500 + 40)  # Map 1.0-1.2 → 40-100

            return DemandSignal(
                name="Pricing Trends",
                score=round(min(100, max(0, score)), 1),
                weight=0.25,
                weighted_score=round(min(100, max(0, score)) * 0.25, 1),
                detail=f"{data_points} data points analyzed" if data_points > 0
                       else "Based on sector growth profile",
            )
        except Exception as e:
            logger.warning(f"Pricing signal error: {e}")
            return DemandSignal(
                name="Pricing Trends", score=50, weight=0.25,
                weighted_score=12.5, detail="Insufficient data",
            )

    async def _competition_signal(self, sector: str, wilaya_code: Optional[str]) -> DemandSignal:
        """
        Estimate competition density from geo places data.
        Some competition = healthy demand; too much = saturated.
        """
        if self.geo_service and wilaya_code:
            try:
                wilaya = await self.db.execute(
                    select(Wilaya).where(Wilaya.code == wilaya_code)
                )
                w = wilaya.scalar_one_or_none()
                if w and w.latitude and w.longitude:
                    # Map sector to place type
                    type_map = {
                        "commerce": "store", "manufacturing": "store",
                        "services": "restaurant", "health": "hospital",
                        "education": "school", "tourism": "hotel",
                    }
                    place_type = type_map.get(sector)
                    places = await self.geo_service.get_nearby_places(
                        w.latitude, w.longitude, 2000, place_type
                    )
                    count = len(places)
                    # Sweet spot: 5-15 competitors = high demand, <3 = low, >20 = saturated
                    if count == 0:
                        score = 30  # No competition — might mean no demand
                    elif count <= 5:
                        score = 50 + count * 6  # Moderate
                    elif count <= 15:
                        score = 80  # Healthy competition
                    else:
                        score = max(40, 90 - (count - 15) * 3)  # Saturating

                    return DemandSignal(
                        name="Competition Density",
                        score=round(score, 1), weight=0.20,
                        weighted_score=round(score * 0.20, 1),
                        detail=f"{count} competitors in 2km radius",
                    )
            except Exception as e:
                logger.warning(f"Competition signal geo error: {e}")

        # Fallback: use sector profile
        profile = SECTOR_PROFILES.get(sector, {})
        base = profile.get("base_demand", 60)
        return DemandSignal(
            name="Competition Density",
            score=round(base * 0.85, 1), weight=0.20,
            weighted_score=round(base * 0.85 * 0.20, 1),
            detail="Based on sector averages (no geo data)",
        )

    async def _demographics_signal(self, sector: str, wilaya_code: Optional[str]) -> DemandSignal:
        """
        Score based on wilaya population and urbanization.
        Larger populations with higher urban rate = more demand for urban sectors.
        """
        profile = SECTOR_PROFILES.get(sector, {})
        urban_factor = profile.get("urban_factor", 1.0)

        if wilaya_code:
            result = await self.db.execute(
                select(Wilaya).where(Wilaya.code == wilaya_code)
            )
            w = result.scalar_one_or_none()
            if w and w.population:
                # Scale: 100k pop = 40, 500k = 60, 1M+ = 80, 4M+ = 95
                pop_score = min(95, 30 + math.log10(max(w.population, 1000)) * 12)

                # Urban adjustment
                is_urban = w.region in ("North", "Central") if w.region else True
                location_factor = urban_factor if is_urban else profile.get("rural_factor", 1.0)
                score = pop_score * location_factor

                return DemandSignal(
                    name="Demographics",
                    score=round(min(100, max(0, score)), 1), weight=0.20,
                    weighted_score=round(min(100, max(0, score)) * 0.20, 1),
                    detail=f"Population: {w.population:,} ({w.region or 'N/A'} region)",
                )

        # Fallback
        return DemandSignal(
            name="Demographics", score=55, weight=0.20,
            weighted_score=11.0, detail="National average (no wilaya specified)",
        )

    async def _activity_signal(self, sector: str, wilaya_code: Optional[str]) -> DemandSignal:
        """
        Use GeoIntelligenceService's activity score for the location.
        """
        if self.geo_service and wilaya_code:
            try:
                wilaya = await self.db.execute(
                    select(Wilaya).where(Wilaya.code == wilaya_code)
                )
                w = wilaya.scalar_one_or_none()
                if w and w.latitude and w.longitude:
                    activity = await self.geo_service.compute_activity_score(
                        w.latitude, w.longitude, 2000
                    )
                    return DemandSignal(
                        name="Area Activity",
                        score=float(activity.score), weight=0.20,
                        weighted_score=round(activity.score * 0.20, 1),
                        detail=f"Activity: {activity.label} ({activity.place_count} places)",
                    )
            except Exception as e:
                logger.warning(f"Activity signal error: {e}")

        return DemandSignal(
            name="Area Activity", score=50, weight=0.20,
            weighted_score=10.0, detail="No geo data available",
        )

    async def _economic_signal(self, sector: str, wilaya_code: Optional[str]) -> DemandSignal:
        """
        Economic indicators from ingested macro data (GDP growth, investment rates).
        Falls back to sector growth trend profile.
        """
        try:
            # Check for macro indicators in the database
            result = await self.db.execute(
                select(func.count(TimeSeriesData.id)).where(
                    TimeSeriesData.source.ilike("%economic%")
                )
            )
            macro_count = result.scalar() or 0

            if macro_count > 0:
                score = 65  # Base with data available
            else:
                # Use sector growth trend as proxy
                profile = SECTOR_PROFILES.get(sector, {})
                growth = profile.get("growth_trend", 1.0)
                # Map growth 1.0-1.2 → 30-90
                score = 30 + (growth - 1.0) * 300
        except Exception:
            score = 50

        return DemandSignal(
            name="Economic Indicators",
            score=round(min(100, max(0, score)), 1), weight=0.15,
            weighted_score=round(min(100, max(0, score)) * 0.15, 1),
            detail=f"Based on {'macro data' if (macro_count if 'macro_count' in dir() else 0) > 0 else 'sector growth trend'}",
        )

    # ------------------------------------------------------------------
    # Composite scoring
    # ------------------------------------------------------------------

    async def compute_demand_score(
        self, sector: str, wilaya_code: Optional[str] = None
    ) -> DemandScore:
        """Compute composite 0-100 demand score from all signals."""
        signals = await self._gather_signals(sector, wilaya_code)

        total = sum(s.weighted_score for s in signals)
        score = min(100, max(0, round(total)))

        if score >= 80:
            label, rec = "Very High", f"Strong demand for {sector} — excellent opportunity"
        elif score >= 60:
            label, rec = "High", f"Good demand for {sector} — favorable conditions"
        elif score >= 40:
            label, rec = "Moderate", f"Average demand for {sector} — viable with differentiation"
        else:
            label, rec = "Low", f"Weak demand for {sector} — consider alternatives"

        wilaya_name = WILAYAS.get(wilaya_code, wilaya_code) if wilaya_code else None

        return DemandScore(
            sector=sector,
            wilaya_code=wilaya_code,
            wilaya_name=wilaya_name,
            score=score,
            label=label,
            recommendation=rec,
            signals=signals,
        )

    async def _gather_signals(
        self, sector: str, wilaya_code: Optional[str]
    ) -> List[DemandSignal]:
        """Gather all 5 signals."""
        signals = [
            await self._pricing_signal(sector, wilaya_code),
            await self._competition_signal(sector, wilaya_code),
            await self._demographics_signal(sector, wilaya_code),
            await self._activity_signal(sector, wilaya_code),
            await self._economic_signal(sector, wilaya_code),
        ]
        return signals

    # ------------------------------------------------------------------
    # Sector opportunities
    # ------------------------------------------------------------------

    async def get_sector_opportunities(
        self, wilaya_code: Optional[str] = None, limit: int = 10
    ) -> List[SectorOpportunity]:
        """Rank all sectors by demand score for a location."""
        results = []
        for sector_slug, profile in SECTOR_PROFILES.items():
            ds = await self.compute_demand_score(sector_slug, wilaya_code)
            results.append(
                SectorOpportunity(
                    rank=0,  # assigned below
                    sector=sector_slug,
                    sector_name=profile["name"],
                    score=ds.score,
                    label=ds.label,
                    key_signals=[
                        s.detail for s in sorted(ds.signals, key=lambda x: -x.weighted_score)[:3]
                    ],
                )
            )

        results.sort(key=lambda x: -x.score)
        for i, opp in enumerate(results):
            opp.rank = i + 1

        return results[:limit]

    # ------------------------------------------------------------------
    # Feasibility report
    # ------------------------------------------------------------------

    async def get_feasibility_report(
        self, sector: str, wilaya_code: Optional[str] = None
    ) -> FeasibilityReport:
        """Full feasibility report combining demand + geo + competition."""
        demand = await self.compute_demand_score(sector, wilaya_code)

        activity_score = None
        competition_count = None
        avg_rating = None

        if self.geo_service and wilaya_code:
            try:
                w_result = await self.db.execute(
                    select(Wilaya).where(Wilaya.code == wilaya_code)
                )
                w = w_result.scalar_one_or_none()
                if w and w.latitude and w.longitude:
                    activity = await self.geo_service.compute_activity_score(
                        w.latitude, w.longitude, 2000
                    )
                    activity_score = activity.score

                    places = await self.geo_service.get_nearby_places(
                        w.latitude, w.longitude, 2000
                    )
                    competition_count = len(places)
                    rated = [p for p in places if p.rating]
                    avg_rating = (
                        round(sum(p.rating for p in rated) / len(rated), 1)
                        if rated else None
                    )
            except Exception as e:
                logger.warning(f"Feasibility geo error: {e}")

        # Verdict logic
        if demand.score >= 75 and (activity_score is None or activity_score >= 40):
            verdict = "Highly Favorable"
        elif demand.score >= 55:
            verdict = "Feasible"
        elif demand.score >= 35:
            verdict = "Risky"
        else:
            verdict = "Not Recommended"

        summary = (
            f"{sector.replace('_', ' ').title()} in "
            f"{demand.wilaya_name or 'Algeria'} shows "
            f"{demand.label.lower()} demand (score: {demand.score}/100). "
        )
        if competition_count is not None:
            summary += f"{competition_count} competitors nearby. "
        summary += f"Verdict: {verdict}."

        return FeasibilityReport(
            sector=sector,
            wilaya_code=wilaya_code,
            wilaya_name=demand.wilaya_name,
            demand_score=demand,
            activity_score=activity_score,
            competition_count=competition_count,
            avg_competitor_rating=avg_rating,
            verdict=verdict,
            summary=summary,
        )
