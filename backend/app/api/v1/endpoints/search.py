from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.schemas.search import SearchAnalysisRequest, SearchAnalysisResponse
from app.schemas.dynamic_layout import DynamicLayoutResponse
from app.services.search_service import SearchService
from app.services.layout_generator_service import LayoutGeneratorService

router = APIRouter()

@router.post("/analyze", response_model=SearchAnalysisResponse)
async def analyze_search_query(
    request: SearchAnalysisRequest,
):
    """
    Analyze a search query using AI to extract intent and structured data.
    """
    service = SearchService()
    
    analysis = await service.analyze_query(request.query)
    
    return SearchAnalysisResponse(
        original_query=request.query,
        analysis=analysis,
        suggested_layout=None
    )


@router.post("/dynamic-layout", response_model=DynamicLayoutResponse)
async def generate_dynamic_layout(
    request: SearchAnalysisRequest,
):
    """
    Generate a dynamic data explorer layout based on a search query.
    Returns widget configurations with AI-generated contextual data.
    """
    try:
        service = LayoutGeneratorService()
        layout = await service.generate_layout(request.query)
        return layout
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

