# ============================================
# Boussole - Analytics Service
# ============================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime

from app.models.sector import Sector
from app.models.indicator import Indicator
from app.models.data_point import DataPoint


class AnalyticsService:
    """
    Service layer for analytics operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_sector_summary(
        self,
        sector_slug: str,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        region: Optional[str] = None
    ) -> Optional[dict]:
        """
        Get a summary of analytics for a specific sector.
        """
        # Get sector
        sector_result = await self.db.execute(
            select(Sector).where(Sector.slug == sector_slug)
        )
        sector = sector_result.scalar_one_or_none()
        
        if not sector:
            return None
        
        # Get indicators for this sector
        indicators_result = await self.db.execute(
            select(Indicator).where(
                and_(
                    Indicator.sector_id == sector.id,
                    Indicator.is_active == True
                )
            )
        )
        indicators = indicators_result.scalars().all()
        
        # Build query for data points
        query = select(DataPoint).where(
            DataPoint.indicator_id.in_([ind.id for ind in indicators])
        )
        
        if period_start:
            query = query.where(DataPoint.period >= period_start)
        
        if period_end:
            query = query.where(DataPoint.period <= period_end)
        
        if region:
            query = query.where(DataPoint.region == region)
        
        data_points_result = await self.db.execute(query)
        data_points = data_points_result.scalars().all()
        
        # Calculate summary statistics
        values = [dp.value for dp in data_points]
        
        summary = {
            "sector": {
                "id": sector.id,
                "slug": sector.slug,
                "name_en": sector.name_en,
                "name_fr": sector.name_fr,
                "name_ar": sector.name_ar,
                "icon": sector.icon,
                "color": sector.color,
            },
            "indicators_count": len(indicators),
            "data_points_count": len(data_points),
            "statistics": {
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "avg": sum(values) / len(values) if values else None,
                "count": len(values),
            },
            "period": {
                "start": period_start,
                "end": period_end,
            },
            "region": region,
        }
        
        return summary
    
    async def get_sector_trends(
        self,
        sector_slug: str,
        indicator_slug: Optional[str] = None,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
        region: Optional[str] = None
    ) -> List[dict]:
        """
        Get trend data for a specific sector.
        """
        # Get sector
        sector_result = await self.db.execute(
            select(Sector).where(Sector.slug == sector_slug)
        )
        sector = sector_result.scalar_one_or_none()
        
        if not sector:
            return []
        
        # Get indicators
        query = select(Indicator).where(
            and_(
                Indicator.sector_id == sector.id,
                Indicator.is_active == True
            )
        )
        
        if indicator_slug:
            query = query.where(Indicator.slug == indicator_slug)
        
        indicators_result = await self.db.execute(query)
        indicators = indicators_result.scalars().all()
        
        # Get data points
        dp_query = select(DataPoint).where(
            DataPoint.indicator_id.in_([ind.id for ind in indicators])
        )
        
        if period_start:
            dp_query = dp_query.where(DataPoint.period >= period_start)
        
        if period_end:
            dp_query = dp_query.where(DataPoint.period <= period_end)
        
        if region:
            dp_query = dp_query.where(DataPoint.region == region)
        
        dp_query = dp_query.order_by(DataPoint.period)
        
        data_points_result = await self.db.execute(dp_query)
        data_points = data_points_result.scalars().all()
        
        # Build trend data
        trends = []
        for dp in data_points:
            indicator = next((ind for ind in indicators if ind.id == dp.indicator_id), None)
            if indicator:
                trends.append({
                    "period": dp.period,
                    "value": dp.value,
                    "indicator": {
                        "id": indicator.id,
                        "slug": indicator.slug,
                        "name_en": indicator.name_en,
                        "name_fr": indicator.name_fr,
                        "name_ar": indicator.name_ar,
                        "unit": indicator.unit,
                    },
                    "region": dp.region,
                })
        
        return trends
    
    async def get_sector_comparison(
        self,
        sector_slug: str,
        compare_with: List[str],
        indicator_slug: Optional[str] = None,
        period: Optional[str] = None
    ) -> dict:
        """
        Compare a sector with other sectors.
        """
        # Get main sector
        main_sector_result = await self.db.execute(
            select(Sector).where(Sector.slug == sector_slug)
        )
        main_sector = main_sector_result.scalar_one_or_none()
        
        if not main_sector:
            return {}
        
        # Get comparison sectors
        compare_sectors_result = await self.db.execute(
            select(Sector).where(Sector.slug.in_(compare_with))
        )
        compare_sectors = compare_sectors_result.scalars().all()
        
        # Get indicators for all sectors
        all_sector_ids = [main_sector.id] + [s.id for s in compare_sectors]
        
        query = select(Indicator).where(
            and_(
                Indicator.sector_id.in_(all_sector_ids),
                Indicator.is_active == True
            )
        )
        
        if indicator_slug:
            query = query.where(Indicator.slug == indicator_slug)
        
        indicators_result = await self.db.execute(query)
        indicators = indicators_result.scalars().all()
        
        # Get data points
        dp_query = select(DataPoint).where(
            DataPoint.indicator_id.in_([ind.id for ind in indicators])
        )
        
        if period:
            dp_query = dp_query.where(DataPoint.period == period)
        
        data_points_result = await self.db.execute(dp_query)
        data_points = data_points_result.scalars().all()
        
        # Build comparison data
        comparison = {
            "main_sector": {
                "id": main_sector.id,
                "slug": main_sector.slug,
                "name_en": main_sector.name_en,
                "name_fr": main_sector.name_fr,
                "name_ar": main_sector.name_ar,
                "color": main_sector.color,
            },
            "compare_with": [
                {
                    "id": s.id,
                    "slug": s.slug,
                    "name_en": s.name_en,
                    "name_fr": s.name_fr,
                    "name_ar": s.name_ar,
                    "color": s.color,
                }
                for s in compare_sectors
            ],
            "period": period,
            "data": [],
        }
        
        # Group data points by sector
        for dp in data_points:
            indicator = next((ind for ind in indicators if ind.id == dp.indicator_id), None)
            if indicator:
                sector = next(
                    (s for s in [main_sector] + compare_sectors if s.id == indicator.sector_id),
                    None
                )
                if sector:
                    comparison["data"].append({
                        "sector_slug": sector.slug,
                        "indicator_slug": indicator.slug,
                        "value": dp.value,
                        "unit": indicator.unit,
                    })
        
        return comparison
    
    async def get_region_summary(
        self,
        region_code: str,
        period: Optional[str] = None
    ) -> Optional[dict]:
        """
        Get a summary of analytics for a specific region.
        """
        # Build query for data points
        query = select(DataPoint).where(DataPoint.region_code == region_code)
        
        if period:
            query = query.where(DataPoint.period == period)
        
        data_points_result = await self.db.execute(query)
        data_points = data_points_result.scalars().all()
        
        if not data_points:
            return None
        
        # Get unique regions from data points
        regions = set(dp.region for dp in data_points if dp.region)
        
        # Calculate summary statistics
        values = [dp.value for dp in data_points]
        
        summary = {
            "region_code": region_code,
            "region_name": list(regions)[0] if regions else None,
            "data_points_count": len(data_points),
            "statistics": {
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "avg": sum(values) / len(values) if values else None,
                "count": len(values),
            },
            "period": period,
        }
        
        return summary
    
    async def get_indicator_forecast(
        self,
        indicator_id: int,
        periods: int = 12
    ) -> Optional[dict]:
        """
        Get forecast data for an indicator.
        
        Note: This is a placeholder for actual forecasting logic.
        In production, you would implement time series forecasting
        using libraries like statsmodels, prophet, or scikit-learn.
        """
        # Get indicator
        indicator_result = await self.db.execute(
            select(Indicator).where(Indicator.id == indicator_id)
        )
        indicator = indicator_result.scalar_one_or_none()
        
        if not indicator:
            return None
        
        # Get historical data points
        query = select(DataPoint).where(
            DataPoint.indicator_id == indicator_id
        ).order_by(DataPoint.period.desc()).limit(24)
        
        data_points_result = await self.db.execute(query)
        historical_data = data_points_result.scalars().all()
        
        if len(historical_data) < 3:
            return None
        
        # Placeholder: Simple linear extrapolation
        # In production, implement proper time series forecasting
        last_values = [dp.value for dp in historical_data[:3]]
        avg_change = (last_values[0] - last_values[-1]) / len(last_values)
        
        forecast_data = []
        last_period = historical_data[0].period
        
        for i in range(1, periods + 1):
            forecast_value = last_values[0] + (avg_change * i)
            forecast_data.append({
                "period": f"forecast-{i}",
                "value": forecast_value,
                "is_forecast": True,
            })
        
        return {
            "indicator": {
                "id": indicator.id,
                "slug": indicator.slug,
                "name_en": indicator.name_en,
                "name_fr": indicator.name_fr,
                "name_ar": indicator.name_ar,
                "unit": indicator.unit,
            },
            "historical_data": [
                {
                    "period": dp.period,
                    "value": dp.value,
                }
                for dp in reversed(historical_data)
            ],
            "forecast": forecast_data,
            "forecast_periods": periods,
        }
    
    async def export_analytics(self, export_config: dict) -> dict:
        """
        Export analytics data in various formats.
        
        Note: This is a placeholder for export functionality.
        In production, implement proper export logic using
        libraries like pandas, openpyxl, or reportlab.
        """
        export_format = export_config.get("format", "json")
        data_type = export_config.get("data_type", "sector")
        filters = export_config.get("filters", {})
        
        # Placeholder implementation
        # In production, generate actual export files
        
        return {
            "format": export_format,
            "data_type": data_type,
            "filters": filters,
            "status": "success",
            "message": f"Export functionality placeholder for {export_format} format",
        }
