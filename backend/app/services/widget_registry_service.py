# ============================================
# Boussole - Widget Registry Service
# ============================================

"""
Service for matching widgets to business intents via tag-based scoring.
This replaces hardcoded dashboard layouts with a dynamic, data-driven approach.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.widget import WidgetDefinition
from app.schemas.intent import BusinessIntent


class WidgetRegistryService:
    """
    Matches WidgetDefinitions to a BusinessIntent by scoring
    each widget based on tag overlap and objective match.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def match_widgets(
        self,
        intent: BusinessIntent,
        limit: int = 10,
    ) -> List[dict]:
        """
        Return widgets ranked by relevance to the given intent.

        Scoring:
          - +2 for each matching data_category tag
          - +3 for each matching objective
          - +1 for wildcard tags/objectives ("*")
          - Final score weighted by widget priority
        """
        # Fetch all active widgets
        result = await self.db.execute(
            select(WidgetDefinition)
            .where(WidgetDefinition.is_active == True)
            .order_by(WidgetDefinition.priority.desc())
        )
        widgets = result.scalars().all()

        intent_categories = [c.value if hasattr(c, "value") else c for c in intent.data_categories]
        intent_objective = intent.objective.value if hasattr(intent.objective, "value") else intent.objective

        scored = []
        for w in widgets:
            score = 0

            # Tag matching
            widget_tags = w.tags or []
            if "*" in widget_tags:
                score += 1  # Wildcard: always matches with low score
            for tag in widget_tags:
                if tag in intent_categories:
                    score += 2

            # Objective matching
            widget_objectives = w.objectives or []
            if "*" in widget_objectives:
                score += 1
            if intent_objective in widget_objectives:
                score += 3

            # Only include widgets that have at least some relevance
            if score > 0:
                # Weight by priority
                final_score = score * (w.priority / 50.0)
                scored.append((w, final_score))

        # Sort by score descending, then by priority
        scored.sort(key=lambda x: (-x[1], -x[0].priority))

        return [
            {
                "slug": w.slug,
                "name": w.name,
                "description": w.description,
                "widget_type": w.widget_type,
                "tags": w.tags,
                "objectives": w.objectives,
                "default_config": w.default_config,
                "required_data": w.required_data,
                "min_data_points": w.min_data_points,
                "relevance_score": round(score, 2),
            }
            for w, score in scored[:limit]
        ]

    async def get_all_widgets(self) -> List[dict]:
        """Return all active widget definitions."""
        result = await self.db.execute(
            select(WidgetDefinition)
            .where(WidgetDefinition.is_active == True)
            .order_by(WidgetDefinition.priority.desc())
        )
        widgets = result.scalars().all()
        return [
            {
                "id": w.id,
                "slug": w.slug,
                "name": w.name,
                "description": w.description,
                "widget_type": w.widget_type,
                "tags": w.tags,
                "objectives": w.objectives,
                "default_config": w.default_config,
                "required_data": w.required_data,
                "min_data_points": w.min_data_points,
                "priority": w.priority,
                "is_active": w.is_active,
            }
            for w in widgets
        ]

    async def get_widget_by_slug(self, slug: str) -> Optional[dict]:
        """Get a single widget by slug."""
        result = await self.db.execute(
            select(WidgetDefinition).where(WidgetDefinition.slug == slug)
        )
        w = result.scalar_one_or_none()
        if not w:
            return None
        return {
            "id": w.id,
            "slug": w.slug,
            "name": w.name,
            "description": w.description,
            "widget_type": w.widget_type,
            "tags": w.tags,
            "objectives": w.objectives,
            "default_config": w.default_config,
            "required_data": w.required_data,
            "min_data_points": w.min_data_points,
            "priority": w.priority,
            "is_active": w.is_active,
        }
