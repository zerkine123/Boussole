# ============================================
# Boussole - Widgets API Endpoint
# ============================================

"""
API endpoints for the Widget Registry.
GET  /api/v1/widgets/        — List all widgets
GET  /api/v1/widgets/{slug}  — Get widget by slug
POST /api/v1/widgets/match   — Match widgets to a parsed BusinessIntent
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.schemas.intent import BusinessIntent, IntentParseRequest
from app.services.widget_registry_service import WidgetRegistryService
from app.services.intent_parser_service import IntentParserService

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_widgets(db: AsyncSession = Depends(get_db)):
    """List all active widget definitions."""
    service = WidgetRegistryService(db)
    return await service.get_all_widgets()


@router.get("/{slug}")
async def get_widget(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a single widget definition by slug."""
    service = WidgetRegistryService(db)
    widget = await service.get_widget_by_slug(slug)
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")
    return widget


@router.post("/match")
async def match_widgets(
    request: IntentParseRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Parse a query into a BusinessIntent, then match it against the widget registry.
    Returns the intent + matched widgets ranked by relevance.
    """
    try:
        # Step 1: Parse the query into structured intent
        parser = IntentParserService()
        intent = await parser.parse(query=request.query, context=request.context)

        # Step 2: Match widgets from the registry
        registry = WidgetRegistryService(db)
        widgets = await registry.match_widgets(intent)

        return {
            "intent": intent.model_dump(),
            "widgets": widgets,
            "provider": parser.get_provider_name(),
            "model": parser.get_model_name(),
        }
    except ValueError as e:
        raise HTTPException(status_code=503, detail=f"LLM provider not available: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Widget matching failed: {e}")
