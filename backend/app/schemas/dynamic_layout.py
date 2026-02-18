from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class WidgetConfig(BaseModel):
    """Configuration for a single UI widget."""
    type: str = Field(..., description="Widget type: hero, kpi_grid, bar_chart, line_chart, pie_chart, data_table, insight_card")
    title: Optional[str] = None
    subtitle: Optional[str] = None
    data: Any = None
    config: Optional[Dict[str, Any]] = None

class DynamicLayoutResponse(BaseModel):
    """Full layout response for the dynamic data explorer."""
    query: str
    title: str
    subtitle: str
    icon: str = "📊"
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    location: Optional[str] = None
    location_name: Optional[str] = None
    widgets: List[WidgetConfig]
