# ============================================
# Boussole - Dashboard Endpoints
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.schemas.metric import (
    Metric,
    MetricWithWilaya,
    DashboardKPI,
    WilayaHeatmapData,
)
from app.services.data_service import DataService
from app.core.deps import get_current_user
from app.models.user import User
from app.models.sector import Sector
from app.models.wilaya import Wilaya
from app.services.llm_adapter import get_llm_adapter
from app.schemas.widgets import DashboardLayoutResponse
import json

router = APIRouter()


@router.get("/kpis", response_model=List[DashboardKPI])
async def get_dashboard_kpis(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    sector_slug: Optional[str] = Query(None, description="Filter by sector"),
    limit: int = Query(6, ge=1, le=20, description="Number of KPIs to return"),
):
    """
    Get dashboard KPI cards based on user preferences.
    
    Returns top metrics by value or change, grouped by sector if specified.
    """
    # Build query
    query = select(Metric).where(Metric.is_verified == True)
    
    if sector_slug:
        # Join with sector to filter
        query = query.join(Metric.sector).where(Sector.slug == sector_slug)
    
    query = query.order_by(Metric.value.desc()).limit(limit)
    
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    # Format as KPI cards
    kpis = []
    for metric in metrics:
        # Determine trend icon and color
        trend_icon = "trending-up" if metric.trend == "up" else "trending-down" if metric.trend == "down" else "minus"
        trend_color = "#22c55e" if metric.trend == "up" else "#ef4444" if metric.trend == "down" else "#6b7280"
        
        kpis.append(DashboardKPI(
            title=metric.name_en,
            value=metric.value,
            unit=metric.unit,
            change_percent=metric.change_percent,
            trend=metric.trend,
            period=metric.period,
            icon="chart-line",
            color=trend_color,
        ))
    
    return kpis


@router.get("/wilaya-heatmap", response_model=List[WilayaHeatmapData])
async def get_wilaya_heatmap(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    sector_slug: Optional[str] = Query(None, description="Filter by sector"),
    metric_slug: Optional[str] = Query(None, description="Filter by metric"),
    period: Optional[str] = Query(None, description="Filter by period"),
):
    """
    Get Wilaya heatmap data for visualization.
    
    Returns metrics aggregated by Wilaya for map visualization.
    """
    # Build query
    query = select(Metric, Wilaya).join(Metric.wilaya)
    
    if sector_slug:
        query = query.join(Metric.sector).where(Sector.slug == sector_slug)
    
    if metric_slug:
        # This would require a separate relationship or join logic
        # For now, we'll just filter by sector and period
        pass
    
    if period:
        query = query.where(Metric.period == period)
    
    query = query.where(Metric.is_verified == True)
    
    result = await db.execute(query)
    rows = result.all()
    
    # Format as heatmap data
    heatmap_data = []
    for metric, wilaya in rows:
        heatmap_data.append(WilayaHeatmapData(
            wilaya_code=wilaya.code,
            wilaya_name_en=wilaya.name_en,
            wilaya_name_fr=wilaya.name_fr,
            wilaya_name_ar=wilaya.name_ar,
            latitude=wilaya.latitude,
            longitude=wilaya.longitude,
            value=metric.value,
            unit=metric.unit,
        ))
    
    return heatmap_data


@router.get("/metrics", response_model=List[MetricWithWilaya])
async def get_dashboard_metrics(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    sector_slug: Optional[str] = Query(None, description="Filter by sector"),
    wilaya_code: Optional[str] = Query(None, description="Filter by Wilaya code"),
    period_start: Optional[str] = Query(None, description="Start period"),
    period_end: Optional[str] = Query(None, description="End period"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get metrics for dashboard with filters.
    """
    service = DataService(db)
    
    # Get metrics with filters
    # This would require additional query logic
    # For now, we'll return a simplified list
    
    # Placeholder implementation
    # In production, implement proper filtering by sector, Wilaya, and period
    result = await db.execute(
        select(Metric)
        .where(Metric.is_verified == True)
        .order_by(Metric.period.desc())
        .offset(skip)
        .limit(limit)
    )
    metrics = result.scalars().all()
    
    # Format with Wilaya details
    formatted_metrics = []
    for metric in metrics:
        # Get Wilaya name (would require join in production)
        formatted_metrics.append(MetricWithWilaya(
            id=metric.id,
            wilaya_id=metric.wilaya_id,
            slug=metric.slug,
            name_en=metric.name_en,
            name_fr=metric.name_fr,
            name_ar=metric.name_ar,
            value=metric.value,
            unit=metric.unit,
            period=metric.period,
            year=metric.year,
            quarter=metric.quarter,
            change_percent=metric.change_percent,
            change_value=metric.change_value,
            trend=metric.trend,
            is_verified=metric.is_verified,
            is_featured=metric.is_featured,
            created_at=metric.created_at,
            updated_at=metric.updated_at,
            # Placeholder Wilaya details
            wilaya_code="",
            wilaya_name_en="",
            wilaya_name_fr="",
            wilaya_name_ar="",
        ))
    
    return formatted_metrics


@router.get("/summary")
async def get_dashboard_summary(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get dashboard summary statistics.
    """
    # Get total counts
    metrics_count = await db.execute(
        select(func.count(Metric.id)).where(Metric.is_verified == True)
    )
    total_metrics = metrics_count.scalar()
    
    sectors_count = await db.execute(
        select(func.count(Sector.id)).where(Sector.is_active == True)
    )
    total_sectors = sectors_count.scalar()
    
    wilayas_count = await db.execute(
        select(func.count(Wilaya.id)).where(Wilaya.is_active == True)
    )
    total_wilayas = wilayas_count.scalar()
    
    return {
        "total_metrics": total_metrics,
        "total_sectors": total_sectors,
        "total_wilayas": total_wilayas,
        "user_id": current_user.id,
        "user_email": current_user.email,
    }


@router.get("/layout")
async def get_dashboard_layout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Dynamically generates the dashboard widget layout for the user based
    on their onboarding preferences and stated intent using the LLM.
    """
    DEFAULT_LAYOUT = [
        {
            "component": "executive_snapshot",
            "title": "Boussole Market Intelligence",
            "summary_text": "AI indicates anomalous growth in the Agriculture tech sector due to recent tax subsidies.",
            "key_metrics": [
               {"label": "New Entrants", "value": "1,240", "trend": "up"},
               {"label": "State Funding", "value": "2.4B DZD", "trend": "up"},
               {"label": "Risk Score", "value": "Low", "trend": "down"},
               {"label": "Market Saturation", "value": "12%", "trend": "none"}
            ],
            "variant": "blue"
        },
        {
            "component": "kpi_card",
            "metric_slug": "total_companies",
            "title": "Registered Businesses",
            "trend_type": "up",
            "filters": None
        },
        {
            "component": "kpi_card",
            "metric_slug": "active_jobs",
            "title": "Active Job Offers",
            "trend_type": "up",
            "filters": None
        },
        {
            "component": "line_chart",
            "metric_slug": "total_companies",
            "title": "Registration Growth over Time",
            "group_by": "year",
            "filters": None
        },
        {
            "component": "bar_chart",
            "metric_slug": "total_companies",
            "title": "Companies by Sector",
            "group_by": "sector",
            "limit": 5,
            "filters": None
        },
        {
            "component": "data_table",
            "metric_slug": "total_companies",
            "title": "Regional Registration Breakdown",
            "group_by": "wilaya",
            "limit": 10,
            "filters": None
        },
        {
            "component": "insight_panel",
            "insight_text": "Our AI expects a 15% jump in agricultural registrations in the southern wilayas based on the new 2024 government subsidies.",
            "type": "opportunity",
            "title": "AI Market Signal"
        },
        {
            "component": "growth_indicator",
            "metric_slug": "total_companies",
            "title": "Company Registration Growth",
            "filters": None
        },
        {
            "component": "ranking_card",
            "metric_slug": "total_companies",
            "title": "Top Wilayas by Volume",
            "group_by": "wilaya",
            "filter_type": "top",
            "limit": 5,
            "filters": None
        },
        {
            "component": "filter_panel",
            "title": "Dashboard Controls",
            "available_filters": ["sector", "wilaya", "year"]
        }
    ]
    
    preferences = current_user.preferences or {}
    intent_text = preferences.get("intent_text", "")
    sub_sectors = preferences.get("sub_sectors", [])
    search_history = preferences.get("search_history", [])
    
    # If no intent or preferences are provided, return the default layout immediately
    if not intent_text and not sub_sectors:
        return {"layout": DEFAULT_LAYOUT}
    
    try:
        adapter = await get_llm_adapter(db)
        
        schema_json = DashboardLayoutResponse.model_json_schema()
        
        system_prompt = (
            "You are an intelligent dashboard orchestrator for Boussole, an Algerian Business Intelligence platform.\n"
            "Your job is to recommend the optimal dashboard layout based on the user's intent AND search history.\n\n"
            "AVAILABLE COMPONENTS TO CHOOSE FROM:\n"
            "- kpi_card: Single metric volume.\n"
            "- line_chart: Trend over time.\n"
            "- bar_chart: Comparison across categories (e.g. sectors).\n"
            "- choropleth_map: Geographic distribution.\n"
            "- data_table: Raw tabular breakdown.\n"
            "- ranking_card: Top or bottom performers.\n"
            "- growth_indicator: Year-over-Year percentage jumps.\n"
            "- insight_panel: AI-written text summary or warning.\n"
            "- pie_chart: Market share or composition.\n"
            "- stacked_area_chart: Hierarchical trends over time.\n"
            "- radar_chart: Performance profile across multiple axises.\n"
            "- composed_chart: Dual metric comparison (e.g. Bar vs Line).\n"
            "- scatter_plot: Correlation analysis between 2 metrics.\n"
            "- treemap: Deep hierarchical breakdowns.\n"
            "- funnel_chart: Sequential pipeline or conversion flow.\n"
            "- comparison_card: Head-to-Head VS matchup between two entities.\n"
            "- gauge_card: Target completion tracking.\n"
            "- metric_grid: Dense 2x2 grid of 4 top-level KPIs.\n"
            "- sentiment_timeline: Historical timeline of events or milestones.\n\n"
            "VALID METRIC SLUGS (you MUST ONLY use these):\n"
            "total_companies, active_jobs, total_investment, active_projects, jobs_created,\n"
            "revenue, exports, startups, incubators, patents, production, market_share,\n"
            "employment_rate, growth_rate, population\n\n"
            "VALID SECTOR SLUGS FOR FILTERS:\n"
            "agriculture, energy, manufacturing, services, tourism, innovation, consulting,\n"
            "housing, education, health, technology, construction, transport, commerce\n\n"
            "RULES:\n"
            "1. You MUST return ONLY a valid JSON object matching the JSON schema provided below.\n"
            "2. Select 4 to 6 widgets that best match the user's intent, utilizing the advanced charts where highly relevant.\n"
            "3. DO NOT invent metric slugs. ONLY use the ones listed above.\n"
            "4. The frontend registry will use your configuration to fetch real data from the database.\n"
            "5. If a user searched for something recently (e.g. 'agriculture in south'), ensure you pass `sector_slug` or `wilaya_code` inside the widget filters!\n\n"
            f"REQUIRED JSON SCHEMA:\n{schema_json}\n"
        )
        
        user_prompt = (
            f"User Intent: {intent_text}\n"
            f"Interest Sub-sectors: {', '.join(sub_sectors) if sub_sectors else 'None specified'}\n"
            f"Recent Search History: {', '.join(search_history) if search_history else 'No recent searches'}\n\n"
            "Generate the JSON layout object."
        )
        
        response = await adapter.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        
        # Clean potential markdown wrappers
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response.replace("```json", "", 1).replace("```", "").strip()
        elif clean_response.startswith("```"):
            clean_response = clean_response.replace("```", "", 1).replace("```", "").strip()
        import json
        try:
            parsed_json = json.loads(clean_response)
            validated = DashboardLayoutResponse(**parsed_json)
            return validated.model_dump()
        except Exception as json_err:
            print(f"Failed to parse LLM JSON: {json_err}")
            print(f"RAW LLM RESPONSE: {clean_response}")
            
            # Fallback layout
            return {
                "layout": [
                    {
                        "component": "kpi_card",
                        "metric_slug": "total_companies",
                        "title": "Total Entities",
                        "trend_type": "up",
                        "filters": None
                    }
                ]
            }
            
    except Exception as e:
        import logging
        logging.error(f"Failed to generate AI layout: {str(e)}")
        # Silent fallback to default layout on LLM failure
        return {"layout": []}


class GenerateLayoutRequest(BaseModel):
    query: str

@router.post("/layout/generate")
async def generate_ondemand_layout(
    request: GenerateLayoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    On-demand layout generation for the Data Explorer.
    Translates free-text queries into a structured UI layout using 21 widget types.
    """
    try:
        adapter = await get_llm_adapter(db)
        schema_json = DashboardLayoutResponse.model_json_schema()
        
        system_prompt = (
            "You are an intelligent data explorer orchestrator for Boussole, an Algerian Business Intelligence platform.\n"
            "Your job is to translate a user's free-text data query into the optimal analytical dashboard layout.\n\n"
            "AVAILABLE COMPONENTS TO CHOOSE FROM:\n"
            "- executive_snapshot: High-level AI summary header with top 4 metrics. (NEW: Highly recommended as the first widget for any inquiry).\n"
            "- kpi_card: Single metric volume.\n"
            "- line_chart: Trend over time.\n"
            "- bar_chart: Comparison across categories (e.g. sectors or wilayas).\n"
            "- choropleth_map: Geographic distribution across Algeria.\n"
            "- data_table: Raw tabular breakdown.\n"
            "- ranking_card: Top or bottom performers.\n"
            "- growth_indicator: Year-over-Year percentage jumps.\n"
            "- insight_panel: AI-written text summary or warning.\n"
            "- pie_chart: Market share or composition.\n"
            "- stacked_area_chart: Hierarchical trends over time.\n"
            "- radar_chart: Performance profile across multiple axises.\n"
            "- composed_chart: Dual metric comparison (e.g. Bar vs Line).\n"
            "- scatter_plot: Correlation analysis between metrics.\n"
            "- treemap: Deep hierarchical breakdowns.\n"
            "- funnel_chart: Sequential pipeline or conversion flow.\n"
            "- comparison_card: Head-to-Head VS matchup between two entities.\n"
            "- gauge_card: Target completion tracking.\n"
            "- metric_grid: Dense 2x2 grid of 4 top-level KPIs.\n"
            "- sentiment_timeline: Historical timeline of events or milestones.\n\n"
            "VALID METRIC SLUGS (you MUST ONLY use these):\n"
            "total_companies, active_jobs, total_investment, active_projects, jobs_created,\n"
            "revenue, exports, startups, incubators, patents, production, market_share,\n"
            "employment_rate, growth_rate, population\n\n"
            "VALID SECTOR SLUGS FOR FILTERS:\n"
            "agriculture, energy, manufacturing, services, tourism, innovation, consulting,\n"
            "housing, education, health, technology, construction, transport, commerce\n\n"
            "RULES:\n"
            "1. You MUST return ONLY a valid JSON object matching the JSON schema provided below.\n"
            "2. Select 3 to 6 widgets that perfectly answer the user's inquiry.\n"
            "3. For `executive_snapshot`, ALWAYS set `variant: \"green\"` for this explorer interface. Provide a `summary_text` (AI summary of the data) and `key_metrics` (array of objects with label, value, trend).\n"
            "4. DO NOT invent metric slugs. ONLY use the ones listed above.\n"
            "5. If the user mentions a specific sector or wilaya, strictly pass it inside the widget filters!\n\n"
            f"REQUIRED JSON SCHEMA:\n{schema_json}\n"
        )
        
        user_prompt = f"User Query: {request.query}\n\nGenerate the JSON layout object representing the answer."
        
        response = await adapter.complete(system_prompt=system_prompt, user_prompt=user_prompt)
        
        clean_response = response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response.replace("```json", "", 1).replace("```", "").strip()
        elif clean_response.startswith("```"):
            clean_response = clean_response.replace("```", "", 1).replace("```", "").strip()
            
        import json
        parsed_json = json.loads(clean_response)
        validated = DashboardLayoutResponse(**parsed_json)
        return validated.model_dump()
        
    except Exception as e:
        import logging
        logging.error(f"Failed to generate on-demand layout: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to synthesize analysis layout. Please try again.")
