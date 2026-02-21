"""add_geo_widgets

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-19 15:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
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
            'slug': 'geo_activity_heatmap',
            'name': 'Area Activity Heatmap',
            'description': 'Map widget showing activity scores across wilayas and locations',
            'widget_type': 'map',
            'tags': ['demographics', 'infrastructure', 'market_demand'],
            'objectives': ['market_analysis', 'feasibility'],
            'default_config': {'height': 450, 'zoom': 6, 'show_scores': True},
            'priority': 72,
            'required_data': ['geo_activity_scores'],
            'min_data_points': 1,
            'is_active': True,
        },
        {
            'slug': 'nearby_places_table',
            'name': 'Nearby Businesses Table',
            'description': 'Table of nearby businesses with ratings, reviews, and categories',
            'widget_type': 'table',
            'tags': ['competition', 'market_demand'],
            'objectives': ['market_analysis', 'comparison'],
            'default_config': {'rows_per_page': 10, 'sortable': True, 'show_map_pins': True},
            'priority': 68,
            'required_data': ['nearby_places'],
            'min_data_points': 1,
            'is_active': True,
        },
    ])


def downgrade() -> None:
    op.execute(
        "DELETE FROM widget_definitions WHERE slug IN ('geo_activity_heatmap', 'nearby_places_table')"
    )
