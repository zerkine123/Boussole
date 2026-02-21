from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.schemas.search import SearchAnalysisRequest, SearchAnalysisResponse
from app.schemas.dynamic_layout import DynamicLayoutResponse
from app.services.search_service import SearchService
from app.services.layout_generator_service import LayoutGeneratorService

from app.core.deps import get_db, get_current_user_optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

router = APIRouter()

@router.post("/analyze", response_model=SearchAnalysisResponse)
async def analyze_search_query(
    request: SearchAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Analyze a search query using AI to extract intent and structured data.
    """
    service = SearchService(db)
    
    analysis = await service.analyze_query(request.query)
    
    # Track search memory for authenticated users
    if current_user and analysis:
        # Extract a meaningful search topic, fallback to the raw query if needed
        search_topic = analysis.topic or analysis.subtopic or request.query
        
        # Initialize preferences if null
        preferences = current_user.preferences or {}
        
        # Get existing history or start new list
        history = preferences.get("search_history", [])
        
        # Only add if it's new (don't spam the same search)
        if not history or history[-1] != search_topic:
            history.append(search_topic)
            
            # Keep only the last 15 searches to prevent JSON bloat
            if len(history) > 15:
                history = history[-15:]
                
            preferences["search_history"] = history
            
            # Since JSON cols don't always auto-track mutations, explicit re-assign
            current_user.preferences = preferences
            db.add(current_user)
            await db.commit()
            
    return SearchAnalysisResponse(
        original_query=request.query,
        analysis=analysis,
        suggested_layout=None
    )


@router.post("/dynamic-layout", response_model=DynamicLayoutResponse)
async def generate_dynamic_layout(
    request: SearchAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a dynamic data explorer layout based on a search query.
    Returns widget configurations with AI-generated contextual data.
    """
    try:
        print(f"DEBUG: Processing dynamic-layout request for: {request.query}")
        service = LayoutGeneratorService(db)
        layout = await service.generate_layout(request.query)
        print("DEBUG: generate_layout returned")
        return layout
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

