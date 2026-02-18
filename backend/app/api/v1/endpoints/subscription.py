# ============================================
# Boussole - Subscription Endpoints
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.subscription import (
    Subscription,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionWithUser,
    SubscriptionUsage,
    SubscriptionTier,
    CheckoutSessionCreate,
    CheckoutSessionResponse,
)
from app.services.subscription_service import SubscriptionService
from app.core.deps import get_current_user, get_current_superuser

router = APIRouter()


@router.get("/my-subscription", response_model=SubscriptionWithUser)
async def get_my_subscription(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's subscription.
    """
    service = SubscriptionService(db)
    subscription = await service.get_user_subscription(current_user.id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription


@router.get("/usage", response_model=SubscriptionUsage)
async def get_subscription_usage(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get subscription usage statistics.
    """
    service = SubscriptionService(db)
    usage = await service.get_subscription_usage(current_user.id)
    
    return usage


@router.get("/tiers", response_model=List[SubscriptionTier])
async def get_available_tiers(
    db: AsyncSession = Depends(get_db)
):
    """
    Get available subscription tiers.
    """
    service = SubscriptionService(db)
    tiers = await service.get_available_tiers()
    
    return tiers


@router.post("/create", response_model=Subscription, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_superuser = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new subscription (admin only).
    """
    service = SubscriptionService(db)
    subscription = await service.create_subscription(subscription_data)
    
    return subscription


@router.put("/{subscription_id}", response_model=Subscription)
async def update_subscription(
    subscription_id: int,
    update_data: SubscriptionUpdate,
    current_superuser = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing subscription (admin only).
    """
    service = SubscriptionService(db)
    subscription = await service.update_subscription(subscription_id, update_data)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return subscription


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_subscription(
    subscription_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel user's subscription.
    """
    service = SubscriptionService(db)
    success = await service.cancel_subscription(subscription_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return None


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    checkout_data: CheckoutSessionCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a Stripe checkout session.
    """
    service = SubscriptionService(db)
    checkout_session = await service.create_checkout_session(current_user.id, checkout_data)
    
    return checkout_session


@router.post("/webhook/stripe", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    event_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    """
    from app.schemas.subscription import StripeWebhookEvent
    
    event = StripeWebhookEvent(**event_data)
    service = SubscriptionService(db)
    success = await service.handle_stripe_webhook(event)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process webhook"
        )
    
    return {"status": "success"}
