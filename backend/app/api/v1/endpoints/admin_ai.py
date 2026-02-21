# ============================================
# Boussole - Admin AI Endpoints
# ============================================

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.deps import get_db, get_current_superuser
from app.models.user import User
from app.models.intent import IntentLog, StaticIntent, SystemPrompt
from app.models.ai_config import AIProviderConfig
from app.schemas.admin_ai import (
    IntentLogResponse, IntentLogUpdate,
    StaticIntentCreate, StaticIntentUpdate, StaticIntentResponse,
    SystemPromptCreate, SystemPromptUpdate, SystemPromptResponse,
    AIProviderConfigCreate, AIProviderConfigUpdate, AIProviderConfigResponse
)
from app.services.llm_adapter import _PROVIDERS

router = APIRouter()

# ============================================
# Intent Logs
# ============================================

@router.get("/audits", response_model=List[IntentLogResponse])
async def read_intent_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """Retrieve all intent logs (Admin only)."""
    query = select(IntentLog).order_by(desc(IntentLog.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.put("/audits/{log_id}", response_model=IntentLogResponse)
async def update_intent_log(
    log_id: int,
    log_in: IntentLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """Update a specific intent log (e.g. for marking accuracy)."""
    result = await db.execute(select(IntentLog).where(IntentLog.id == log_id))
    log_entry = result.scalar_one_or_none()
    
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
        
    update_data = log_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log_entry, field, value)
        
    await db.commit()
    await db.refresh(log_entry)
    return log_entry


# ============================================
# Static Intents
# ============================================

@router.get("/static", response_model=List[StaticIntentResponse])
async def read_static_intents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """Retrieve all static intent mappings."""
    result = await db.execute(select(StaticIntent).order_by(desc(StaticIntent.created_at)))
    return result.scalars().all()

@router.post("/static", response_model=StaticIntentResponse)
async def create_static_intent(
    intent_in: StaticIntentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """Create a new static intent mapping."""
    # Check for exact duplicate keywords
    result = await db.execute(select(StaticIntent).where(StaticIntent.keyword == intent_in.keyword))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="A static intent with this keyword already exists")
        
    db_intent = StaticIntent(**intent_in.model_dump())
    db.add(db_intent)
    await db.commit()
    await db.refresh(db_intent)
    return db_intent

@router.put("/static/{intent_id}", response_model=StaticIntentResponse)
async def update_static_intent(
    intent_id: int,
    intent_in: StaticIntentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """Update a static intent mapping."""
    result = await db.execute(select(StaticIntent).where(StaticIntent.id == intent_id))
    db_intent = result.scalar_one_or_none()
    if not db_intent:
        raise HTTPException(status_code=404, detail="Static intent not found")
        
    update_data = intent_in.model_dump(exclude_unset=True)
    if "keyword" in update_data and update_data["keyword"] != db_intent.keyword:
        # Check collision
        coll_check = await db.execute(select(StaticIntent).where(StaticIntent.keyword == update_data["keyword"]))
        if coll_check.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="A static intent with this keyword already exists")
            
    for field, value in update_data.items():
        setattr(db_intent, field, value)
        
    await db.commit()
    await db.refresh(db_intent)
    return db_intent

@router.delete("/static/{intent_id}")
async def delete_static_intent(
    intent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """Delete a static intent mapping."""
    result = await db.execute(select(StaticIntent).where(StaticIntent.id == intent_id))
    db_intent = result.scalar_one_or_none()
    if not db_intent:
        raise HTTPException(status_code=404, detail="Static intent not found")
        
    await db.delete(db_intent)
    await db.commit()
    return {"ok": True}


# ============================================
# System Prompts
# ============================================

@router.get("/prompts", response_model=List[SystemPromptResponse])
async def read_system_prompts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """Retrieve all system prompts."""
    # Group by name, get latest version
    result = await db.execute(select(SystemPrompt).order_by(SystemPrompt.name, desc(SystemPrompt.version)))
    
    # Simple manual distinct logic since postgres DISTINCT ON is harder in raw SA without specific dialect
    prompts = result.scalars().all()
    seen_names = set()
    latest_prompts = []
    
    for prompt in prompts:
        if prompt.name not in seen_names:
            seen_names.add(prompt.name)
            latest_prompts.append(prompt)
            
    return latest_prompts

@router.post("/prompts", response_model=SystemPromptResponse)
async def create_system_prompt_version(
    prompt_in: SystemPromptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """Create a new version of a system prompt, or initialize a new one."""
    result = await db.execute(
        select(SystemPrompt)
        .where(SystemPrompt.name == prompt_in.name)
        .order_by(desc(SystemPrompt.version))
    )
    latest = result.scalars().first()
    
    version = (latest.version + 1) if latest else 1
    
    # If adding a new version, mark others as inactive (optional behavior, depending on requirements)
    if latest:
        latest.is_active = False
        db.add(latest)

    db_prompt = SystemPrompt(
        **prompt_in.model_dump(),
        version=version,
        updated_by=current_user.id
    )
    db.add(db_prompt)
    await db.commit()
    await db.refresh(db_prompt)
    return db_prompt

# ============================================
# AI Provider Configurations
# ============================================

@router.get("/providers", response_model=List[AIProviderConfigResponse])
async def read_ai_providers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Get all AI provider configurations."""
    query = select(AIProviderConfig).order_by(AIProviderConfig.id.asc())
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/providers", response_model=AIProviderConfigResponse)
async def create_ai_provider(
    provider_in: AIProviderConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Create a new AI provider config."""
    # If this is active, deactivate others
    if provider_in.is_active:
        update_stmt = select(AIProviderConfig).where(AIProviderConfig.is_active == True)
        res = await db.execute(update_stmt)
        for old in res.scalars().all():
            old.is_active = False

    db_provider = AIProviderConfig(**provider_in.model_dump())
    db.add(db_provider)
    await db.commit()
    await db.refresh(db_provider)
    return db_provider

@router.put("/providers/{provider_id}", response_model=AIProviderConfigResponse)
async def update_ai_provider(
    provider_id: int,
    provider_in: AIProviderConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Update an AI provider config."""
    db_provider_query = await db.execute(select(AIProviderConfig).where(AIProviderConfig.id == provider_id))
    db_provider = db_provider_query.scalar_one_or_none()
    
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider config not found")

    update_data = provider_in.model_dump(exclude_unset=True)
    
    # Handle activation rule
    if update_data.get("is_active"):
        update_stmt = select(AIProviderConfig).where(AIProviderConfig.is_active == True, AIProviderConfig.id != provider_id)
        res = await db.execute(update_stmt)
        for old in res.scalars().all():
            old.is_active = False

    for field, value in update_data.items():
        setattr(db_provider, field, value)

    await db.commit()
    await db.refresh(db_provider)
    return db_provider

@router.delete("/providers/{provider_id}", response_model=dict)
async def delete_ai_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Delete an AI provider config."""
    db_provider_query = await db.execute(select(AIProviderConfig).where(AIProviderConfig.id == provider_id))
    db_provider = db_provider_query.scalar_one_or_none()
    
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider config not found")
        
    await db.delete(db_provider)
    await db.commit()
    return {"message": "Provider config deleted successfully"}

@router.post("/providers/test")
async def test_ai_provider(
    provider_in: AIProviderConfigCreate,
    current_user: User = Depends(get_current_superuser)
):
    """Test connection to an AI provider without saving it."""
    provider_name = provider_in.provider_name.lower()
    adapter_cls = _PROVIDERS.get(provider_name)
    if not adapter_cls:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_name}")
    
    try:
        adapter = adapter_cls(
            api_key=provider_in.api_key,
            model_name=provider_in.model_name,
            api_base_url=provider_in.api_base_url
        )
        # Test completion
        response = await adapter.complete(
            system_prompt="You are a helpful test assistant.",
            user_prompt="Say exactly 'OK'",
            max_tokens=10
        )
        return {"success": True, "message": "Connection successful", "response": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
