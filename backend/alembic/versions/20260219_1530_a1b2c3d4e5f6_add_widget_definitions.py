"""add_widget_definitions

Revision ID: a1b2c3d4e5f6
Revises: 08d602bd490d
Create Date: 2026-02-19 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '08d602bd490d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create widget_definitions table
    op.create_table('widget_definitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('widget_type', sa.String(length=50), nullable=False),
        sa.Column('tags', ARRAY(sa.String()), nullable=False),
        sa.Column('objectives', ARRAY(sa.String()), nullable=False),
        sa.Column('default_config', sa.JSON(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('required_data', ARRAY(sa.String()), nullable=True),
        sa.Column('min_data_points', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_widget_definitions_id', 'widget_definitions', ['id'], unique=False)
    op.create_index('ix_widget_definitions_slug', 'widget_definitions', ['slug'], unique=True)
    op.create_index('ix_widget_definitions_widget_type', 'widget_definitions', ['widget_type'], unique=False)
    op.create_index('ix_widget_definitions_is_active', 'widget_definitions', ['is_active'], unique=False)
    op.create_index('ix_widget_definitions_priority', 'widget_definitions', ['priority'], unique=False)

    # Seed initial widget definitions
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
            'slug': 'hero_summary',
            'name': 'Hero Summary',
            'description': 'Top-level summary card with title, subtitle, and key metrics overview',
            'widget_type': 'hero',
            'tags': ['*'],
            'objectives': ['*'],
            'default_config': {'height': 200, 'style': 'gradient'},
            'priority': 100,
            'required_data': [],
            'min_data_points': 0,
            'is_active': True,
        },
        {
            'slug': 'kpi_overview',
            'name': 'KPI Overview Grid',
            'description': 'Grid of key performance indicators with values and trends',
            'widget_type': 'kpi_grid',
            'tags': ['market_demand', 'finance'],
            'objectives': ['market_analysis', 'feasibility'],
            'default_config': {'columns': 4, 'height': 120},
            'priority': 90,
            'required_data': ['metric_kpis'],
            'min_data_points': 1,
            'is_active': True,
        },
        {
            'slug': 'sector_bar_chart',
            'name': 'Sector Comparison Bar Chart',
            'description': 'Bar chart comparing metrics across sectors or categories',
            'widget_type': 'bar_chart',
            'tags': ['competition', 'market_demand'],
            'objectives': ['market_analysis', 'comparison'],
            'default_config': {'height': 350, 'color_scheme': 'blue'},
            'priority': 80,
            'required_data': ['indicator_comparison'],
            'min_data_points': 2,
            'is_active': True,
        },
        {
            'slug': 'trend_line_chart',
            'name': 'Trend Line Chart',
            'description': 'Line chart showing data trends over time',
            'widget_type': 'line_chart',
            'tags': ['market_demand', 'finance'],
            'objectives': ['trend_tracking'],
            'default_config': {'height': 350, 'years': 7},
            'priority': 75,
            'required_data': ['indicator_timeseries'],
            'min_data_points': 3,
            'is_active': True,
        },
        {
            'slug': 'insight_card',
            'name': 'AI Insight Card',
            'description': 'AI-generated textual insights and recommendations',
            'widget_type': 'insight_card',
            'tags': ['*'],
            'objectives': ['*'],
            'default_config': {'max_insights': 4},
            'priority': 60,
            'required_data': [],
            'min_data_points': 0,
            'is_active': True,
        },
        {
            'slug': 'competition_table',
            'name': 'Competition Analysis Table',
            'description': 'Sortable table showing competitive landscape data',
            'widget_type': 'table',
            'tags': ['competition'],
            'objectives': ['market_analysis', 'feasibility'],
            'default_config': {'rows_per_page': 10, 'sortable': True},
            'priority': 70,
            'required_data': ['competition_data'],
            'min_data_points': 1,
            'is_active': True,
        },
        {
            'slug': 'geo_heatmap',
            'name': 'Geographic Heatmap',
            'description': 'Map visualization showing data density across wilayas',
            'widget_type': 'map',
            'tags': ['demographics', 'infrastructure'],
            'objectives': ['market_analysis'],
            'default_config': {'height': 400, 'zoom': 5},
            'priority': 65,
            'required_data': ['geographic_data'],
            'min_data_points': 1,
            'is_active': True,
        },
        {
            'slug': 'finance_breakdown',
            'name': 'Finance Breakdown',
            'description': 'Pie chart showing financial distribution or cost breakdown',
            'widget_type': 'pie_chart',
            'tags': ['finance'],
            'objectives': ['feasibility', 'investment'],
            'default_config': {'height': 350, 'show_legend': True},
            'priority': 70,
            'required_data': ['finance_breakdown'],
            'min_data_points': 2,
            'is_active': True,
        },
        {
            'slug': 'labor_radar',
            'name': 'Labor Market Radar',
            'description': 'Radar chart comparing labor market dimensions',
            'widget_type': 'radar',
            'tags': ['labor', 'demographics'],
            'objectives': ['feasibility'],
            'default_config': {'height': 350, 'dimensions': 6},
            'priority': 55,
            'required_data': ['labor_metrics'],
            'min_data_points': 3,
            'is_active': True,
        },
    ])


def downgrade() -> None:
    op.drop_index('ix_widget_definitions_priority', table_name='widget_definitions')
    op.drop_index('ix_widget_definitions_is_active', table_name='widget_definitions')
    op.drop_index('ix_widget_definitions_widget_type', table_name='widget_definitions')
    op.drop_index('ix_widget_definitions_slug', table_name='widget_definitions')
    op.drop_index('ix_widget_definitions_id', table_name='widget_definitions')
    op.drop_table('widget_definitions')
