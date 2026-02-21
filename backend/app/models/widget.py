# ============================================
# Boussole - Widget Definition Model
# ============================================

"""
Database model for the Widget Registry.
Each widget has tags for data categories, supported objectives,
rendering config, and data requirements.
"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from sqlalchemy import DateTime
from app.db.base import Base


class WidgetDefinition(Base):
    """
    Widget definition for the dynamic dashboard registry.
    Widgets are matched to user intents via tags and objectives.
    """

    __tablename__ = "widget_definitions"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Widget type: kpi_grid, bar_chart, line_chart, pie_chart,
    #              table, map, radar, hero, insight_card
    widget_type = Column(String(50), nullable=False, index=True)

    # Tag-based matching — maps to DataCategory enum values
    # e.g. ["finance", "competition", "market_demand"]
    tags = Column(ARRAY(String), nullable=False, default=[])

    # Which business objectives this widget serves
    # e.g. ["market_analysis", "feasibility"]
    objectives = Column(ARRAY(String), nullable=False, default=[])

    # Default rendering configuration (JSON)
    # e.g. {"columns": 2, "height": 300, "color_scheme": "blue"}
    default_config = Column(JSON, default={})

    # Display priority — higher values shown first
    priority = Column(Integer, default=50, index=True)

    # What data the widget needs to render
    # e.g. ["indicator_timeseries", "metric_kpis"]
    required_data = Column(ARRAY(String), default=[])

    # Minimum number of data points needed to render this widget
    min_data_points = Column(Integer, default=1)

    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WidgetDefinition(slug={self.slug}, type={self.widget_type})>"
