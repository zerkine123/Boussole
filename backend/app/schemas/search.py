from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SearchAnalysisRequest(BaseModel):
    query: str
    context: Optional[str] = None

class SearchIntent(BaseModel):
    intent: str = Field(..., description="Primary intent: analytics, market, navigation, general_q, unknown")
    topic: Optional[str] = Field(None, description="Main topic: agriculture, energy, startups, etc.")
    subtopic: Optional[str] = Field(None, description="Specific subtopic: greenhouses, solar panels, etc.")
    location: Optional[str] = Field(None, description="Algerian Wilaya code (01-58) or name")
    filters: Optional[Dict[str, Any]] = Field(default={}, description="Additional filters extracted from query")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score of the analysis")

class SearchAnalysisResponse(BaseModel):
    original_query: str
    analysis: SearchIntent
    suggested_layout: Optional[List[str]] = Field(None, description="Suggested UI components to render")
