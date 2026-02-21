# ============================================
# Boussole - Admin AI Management Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime

# ============================================
# Intent Log Schemas
# ============================================

class IntentLogBase(BaseModel):
    query: str
    provider: str
    model_name: str
    latency_ms: Optional[float] = None
    confidence: Optional[float] = None
    parsed_intent: Dict[str, Any]
    is_accurate: Optional[bool] = None
    feedback_notes: Optional[str] = None

class IntentLogUpdate(BaseModel):
    is_accurate: Optional[bool] = None
    feedback_notes: Optional[str] = None

class IntentLogResponse(IntentLogBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ============================================
# Static Intent Schemas
# ============================================

class StaticIntentBase(BaseModel):
    keyword: str = Field(..., description="Exact phrasing to match (case-insensitive)")
    mapped_intent: Dict[str, Any] = Field(..., description="The BusinessIntent JSON to return")
    is_active: bool = True

class StaticIntentCreate(StaticIntentBase):
    pass

class StaticIntentUpdate(BaseModel):
    keyword: Optional[str] = None
    mapped_intent: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class StaticIntentResponse(StaticIntentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ============================================
# System Prompt Schemas
# ============================================

class SystemPromptBase(BaseModel):
    name: str = Field(..., description="Identifier name of the prompt (e.g. intent_parser)")
    content: str = Field(..., description="The actual LLM system instructions")
    description: Optional[str] = None
    is_active: bool = True

class SystemPromptCreate(SystemPromptBase):
    pass

class SystemPromptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class SystemPromptResponse(SystemPromptBase):
    id: int
    version: int
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ============================================
# AI Provider Config Schemas
# ============================================

class AIProviderConfigBase(BaseModel):
    provider_name: str
    api_key: str
    api_base_url: Optional[str] = None
    model_name: str
    is_active: bool = False

class AIProviderConfigCreate(AIProviderConfigBase):
    pass

class AIProviderConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    model_name: Optional[str] = None
    is_active: Optional[bool] = None

class AIProviderConfigResponse(AIProviderConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
