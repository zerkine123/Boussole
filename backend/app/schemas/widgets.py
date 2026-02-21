from typing import List, Optional, Dict, Literal, Union
from pydantic import BaseModel, Field

# Base Filter Model
class WidgetFilters(BaseModel):
    sector_slug: Optional[str] = Field(None, description="Slug of the sector to filter by")
    wilaya_code: Optional[str] = Field(None, description="Code of the Wilaya to filter by (e.g., '16' for Algiers)")
    start_year: Optional[int] = Field(None, description="Start year for time series data")
    end_year: Optional[int] = Field(None, description="End year for time series data")

# 1. KPI Card
class KPICardWidget(BaseModel):
    component: Literal["kpi_card"] = "kpi_card"
    metric_slug: str = Field(..., description="Slug of the metric to display (e.g., 'total_companies', 'active_jobs')")
    title: str = Field(..., description="User-friendly title for the KPI card")
    trend_type: Literal["up", "down", "neutral", "none"] = Field("none", description="Expected trend arrow visualization")
    filters: Optional[WidgetFilters] = None

# 2. Line Chart
class LineChartWidget(BaseModel):
    component: Literal["line_chart"] = "line_chart"
    metric_slug: str = Field(..., description="Slug of the time-series metric")
    title: str = Field(..., description="Title of the line chart")
    group_by: Literal["year", "month"] = Field("year", description="Time aggregation")
    filters: Optional[WidgetFilters] = None

# 3. Bar Chart
class BarChartWidget(BaseModel):
    component: Literal["bar_chart"] = "bar_chart"
    metric_slug: str = Field(..., description="Slug of the metric")
    title: str = Field(..., description="Title of the bar chart")
    group_by: Literal["sector", "wilaya", "year"] = Field(..., description="Category to group bars by")
    limit: int = Field(5, description="Number of bars to show (e.g., top 5)")
    filters: Optional[WidgetFilters] = None

# 4. Choropleth Map
class ChoroplethMapWidget(BaseModel):
    component: Literal["choropleth_map"] = "choropleth_map"
    metric_slug: str = Field(..., description="Slug of the metric to visualize geographically")
    title: str = Field(..., description="Title of the map")
    filters: Optional[WidgetFilters] = None

# 5. Data Table
class DataTableWidget(BaseModel):
    component: Literal["data_table"] = "data_table"
    metric_slugs: List[str] = Field(..., description="List of metrics to include as columns")
    title: str = Field(..., description="Title of the table")
    group_by: Literal["sector", "wilaya"] = Field(..., description="Primary entity row")
    filters: Optional[WidgetFilters] = None

# 6. Ranking Card
class RankingCardWidget(BaseModel):
    component: Literal["ranking_card"] = "ranking_card"
    metric_slug: str = Field(..., description="Slug of the metric used for ranking")
    title: str = Field(..., description="Title of the ranking card")
    group_by: Literal["sector", "wilaya"] = Field(..., description="Entity being ranked")
    order: Literal["asc", "desc"] = Field("desc", description="Sort order (desc = top winners)")
    limit: int = Field(5, description="Number of items to show")
    filters: Optional[WidgetFilters] = None

# 7. Growth Indicator
class GrowthIndicatorWidget(BaseModel):
    component: Literal["growth_indicator"] = "growth_indicator"
    metric_slug: str = Field(..., description="Slug of the metric")
    title: str = Field(..., description="Title of the growth block")
    comparison: Literal["yoy", "cagr", "mom"] = Field("yoy", description="Year-over-Year, CAGR, or Month-over-Month")
    filters: Optional[WidgetFilters] = None

# 8. Insight Panel
class InsightPanelWidget(BaseModel):
    component: Literal["insight_panel"] = "insight_panel"
    text: str = Field(..., description="AI-generated analytical text explaining a trend or noting an opportunity")
    sentiment: Literal["positive", "negative", "neutral", "warning"] = Field("neutral", description="Color/Icon coding for the insight")

# 9. Filter Panel
class FilterPanelWidget(BaseModel):
    component: Literal["filter_panel"] = "filter_panel"
    allowed_filters: List[Literal["sector", "wilaya", "year"]] = Field(..., description="Which filters to expose to the user")

# 10. Executive Snapshot
class ExecutiveSnapshotWidget(BaseModel):
    component: Literal["executive_snapshot"] = "executive_snapshot"
    title: str = Field(..., description="Title of the snapshot")
    metrics: List[str] = Field(..., description="Up to 4 metric slugs to display in miniature")
    summary: str = Field(..., description="A 1-2 sentence AI summary of the snapshot")
    filters: Optional[WidgetFilters] = None

# 11. Pie Chart
class PieChartWidget(BaseModel):
    component: Literal["pie_chart"] = "pie_chart"
    metric_slug: str = Field(..., description="Slug of the metric (e.g., 'startup_funding')")
    title: str = Field(..., description="Title of the pie chart")
    group_by: Literal["sector", "wilaya", "year"] = Field(..., description="Category for pie slices")
    limit: int = Field(5, description="Number of slices before grouping remaining as 'Others'")
    filters: Optional[WidgetFilters] = None

# 12. Stacked Area Chart
class StackedAreaChartWidget(BaseModel):
    component: Literal["stacked_area_chart"] = "stacked_area_chart"
    metric_slug: str = Field(..., description="Slug of the metric")
    title: str = Field(..., description="Title of the stacked area chart")
    group_by: Literal["year"] = Field("year", description="X-axis category (usually year)")
    stack_by: Literal["sector", "wilaya"] = Field(..., description="Category to stack the areas by")
    filters: Optional[WidgetFilters] = None

# 13. Radar Chart
class RadarChartWidget(BaseModel):
    component: Literal["radar_chart"] = "radar_chart"
    metric_slug: str = Field(..., description="Slug of the metric")
    title: str = Field(..., description="Title of the radar chart")
    group_by: Literal["sector", "wilaya"] = Field(..., description="Category for the radar points (max 8)")
    limit: int = Field(6, description="Max points to plot")
    filters: Optional[WidgetFilters] = None

# 14. Composed Chart
class ComposedChartWidget(BaseModel):
    component: Literal["composed_chart"] = "composed_chart"
    metric_slugs: List[str] = Field(..., description="Exactly two metrics: [primary_bar_metric, secondary_line_metric]")
    title: str = Field(..., description="Title of the chart")
    group_by: Literal["year", "sector", "wilaya"] = Field("year", description="X-axis category")
    limit: int = Field(10, description="Max points to plot")
    filters: Optional[WidgetFilters] = None

# 15. Scatter Plot
class ScatterPlotWidget(BaseModel):
    component: Literal["scatter_plot"] = "scatter_plot"
    metric_slugs: List[str] = Field(..., description="Exactly two or three metrics for [X, Y, (optional)Z bubble size]")
    title: str = Field(..., description="Title of the scatter plot")
    group_by: Literal["sector", "wilaya"] = Field(..., description="Entity defining the points")
    filters: Optional[WidgetFilters] = None

# 16. Treemap
class TreemapWidget(BaseModel):
    component: Literal["treemap"] = "treemap"
    metric_slug: str = Field(..., description="Slug of the hierarchy volume metric")
    title: str = Field(..., description="Title of the hierarchical map")
    group_by: Literal["sector", "wilaya"] = Field(..., description="Category for boxes")
    limit: int = Field(15, description="Max number of boxes")
    filters: Optional[WidgetFilters] = None

# 17. Funnel Chart
class FunnelChartWidget(BaseModel):
    component: Literal["funnel_chart"] = "funnel_chart"
    metric_slugs: List[str] = Field(..., description="Ordered list of sequentially shrinking metrics for conversion steps")
    title: str = Field(..., description="Pipeline/Funnel title")
    filters: Optional[WidgetFilters] = None

# 18. Comparison Card
class ComparisonCardWidget(BaseModel):
    component: Literal["comparison_card"] = "comparison_card"
    metric_slug: str = Field(..., description="Slug of the metric to compare")
    title: str = Field(..., description="Title of head-to-head comparison")
    compare_field: Literal["sector", "wilaya"] = Field(..., description="Which field type the entity codes fall under")
    compare_entities: List[str] = Field(..., description="List of EXACTLY two entity names or codes (e.g. ['Algiers', 'Oran'])")
    filters: Optional[WidgetFilters] = None

# 19. Gauge Card
class GaugeCardWidget(BaseModel):
    component: Literal["gauge_card"] = "gauge_card"
    metric_slug: str = Field(..., description="Metric slug to gauge")
    title: str = Field(..., description="Title (e.g., Progress to Goal)")
    target_value: int = Field(..., description="Absolute numeric target to fill the gauge (100% mark)")
    filters: Optional[WidgetFilters] = None

# 20. Metric Grid
class MetricGridWidget(BaseModel):
    component: Literal["metric_grid"] = "metric_grid"
    metric_slugs: List[str] = Field(..., description="List of Exactly 4 metric slugs to display in 2x2 grid")
    title: str = Field(..., description="Title of the KPI cluster")
    filters: Optional[WidgetFilters] = None

# 21. Sentiment/Event Timeline
class SentimentTimelineWidget(BaseModel):
    component: Literal["sentiment_timeline"] = "sentiment_timeline"
    metric_slug: str = Field(..., description="Slug of metric. Automatically mapped across years.")
    title: str = Field(..., description="Title of timeline history")
    limit: int = Field(5, description="Max historical points to show")
    filters: Optional[WidgetFilters] = None

# Union of all widget types for the final layout array
AnyWidget = Union[
    KPICardWidget,
    LineChartWidget,
    BarChartWidget,
    ChoroplethMapWidget,
    DataTableWidget,
    RankingCardWidget,
    GrowthIndicatorWidget,
    InsightPanelWidget,
    FilterPanelWidget,
    ExecutiveSnapshotWidget,
    PieChartWidget,
    StackedAreaChartWidget,
    RadarChartWidget,
    ComposedChartWidget,
    ScatterPlotWidget,
    TreemapWidget,
    FunnelChartWidget,
    ComparisonCardWidget,
    GaugeCardWidget,
    MetricGridWidget,
    SentimentTimelineWidget
]

class DashboardLayoutResponse(BaseModel):
    layout: List[AnyWidget] = Field(..., description="Ordered list of configured widgets to render on the dashboard")
