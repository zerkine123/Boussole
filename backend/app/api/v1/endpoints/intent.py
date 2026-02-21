# ============================================
# Boussole - Intent API Endpoint
# ============================================

"""
API endpoint for parsing business queries into structured intents.
POST /api/v1/intent/parse
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.intent import IntentParseRequest, IntentParseResponse
from app.services.intent_parser_service import IntentParserService
from app.core.deps import get_db

router = APIRouter()


@router.post("/parse", response_model=IntentParseResponse)
async def parse_intent(
    request: IntentParseRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Parse a natural language business query into a structured BusinessIntent.

    This is the core brain of Boussole — it converts queries like
    "bakery in Tébessa" into structured JSON with sector, location,
    objective, and required data categories.
    """
    try:
        service = IntentParserService(db=db)
        intent = await service.parse(
            query=request.query,
            context=request.context,
        )

        return IntentParseResponse(
            intent=intent,
            provider=service.get_provider_name(),
            model=service.get_model_name(),
        )
    except ValueError as e:
        raise HTTPException(status_code=503, detail=f"LLM provider not available: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent parsing failed: {e}")
