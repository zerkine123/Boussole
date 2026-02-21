"""add_demand_widgets

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-19 16:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    widgets_table = sa.table('widget_definitions',
        sa.column('slug', sa.String),
        sa.column('name', sa.String),
        sa.column('description', sa.Text),
        sa.column('widget_type', sa.String),
        sa.column('tags', ARRAY(sa.String)),
        sa.column('objectives', ARRAY(sa.String)),
        sa.column('default_config', sa.JSON),
        sa.column('priority', sa.Integer),
        sa.column('required_data', ARRAY(sa.String)),
        sa.column('min_data_points', sa.Integer),
        sa.column('is_active', sa.Boolean),
    )

    op.bulk_insert(widgets_table, [
        {
            'slug': 'demand_score_gauge',
            'name': 'Demand Score Gauge',
            'description': 'Circular gauge showing 0-100 market demand score with signal breakdown',
            'widget_type': 'gauge',
            'tags': ['market_demand', 'finance', 'demographics'],
            'objectives': ['market_analysis', 'feasibility'],
            'default_config': {'height': 280, 'show_breakdown': True, 'color_scale': ['#ef4444', '#f59e0b', '#22c55e']},
            'priority': 85,
            'required_data': ['demand_score'],
            'min_data_points': 1,
            'is_active': True,
        },
        {
            'slug': 'opportunity_ranking',
            'name': 'Sector Opportunity Ranking',
            'description': 'Ranked table of sectors by demand score and opportunity signals',
            'widget_type': 'table',
            'tags': ['market_demand', 'competition', '*'],
            'objectives': ['market_analysis', 'comparison'],
            'default_config': {'rows_per_page': 10, 'sortable': True, 'show_score_bar': True},
            'priority': 78,
            'required_data': ['sector_opportunities'],
            'min_data_points': 1,
            'is_active': True,
        },
        {
            'slug': 'feasibility_breakdown',
            'name': 'Feasibility Signal Radar',
            'description': 'Radar chart showing demand signal breakdown across 5 dimensions',
            'widget_type': 'radar',
            'tags': ['market_demand', 'competition', 'demographics', 'infrastructure'],
            'objectives': ['feasibility', 'market_analysis'],
            'default_config': {'height': 350, 'show_values': True},
            'priority': 75,
            'required_data': ['demand_signals'],
            'min_data_points': 5,
            'is_active': True,
        },
    ])


def downgrade() -> None:
    op.execute(
        "DELETE FROM widget_definitions WHERE slug IN ('demand_score_gauge', 'opportunity_ranking', 'feasibility_breakdown')"
    )
