# ============================================
# Boussole - Subscription Schemas
# ============================================

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class SubscriptionBase(BaseModel):
    """Base Subscription schema with common fields."""
    tier: str = Field(..., pattern="^(free|pro|enterprise)$")
    price: float = Field(..., ge=0, description="Monthly price in DZD")
    currency: str = Field(default="DZD")
    billing_interval: str = Field(default="month", pattern="^(month|year)$")


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a new subscription (admin only)."""
    user_id: int = Field(..., gt=0)
    stripe_customer_id: Optional[str] = Field(None, max_length=255)
    stripe_subscription_id: Optional[str] = Field(None, max_length=255)
    stripe_price_id: Optional[str] = Field(None, max_length=255)
    status: str = Field(default="active", pattern="^(active|canceled|past_due|trialing)$")
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    api_rate_limit: Optional[int] = Field(None, ge=0)
    data_export_limit: Optional[int] = Field(None, ge=0)
    ai_queries_limit: Optional[int] = Field(None, ge=0)
    features: Optional[str] = Field(None, description="JSON string of enabled features")
    notes: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    """Schema for updating an existing subscription."""
    tier: Optional[str] = Field(None, pattern="^(free|pro|enterprise)$")
    status: Optional[str] = Field(None, pattern="^(active|canceled|past_due|trialing)$")
    api_rate_limit: Optional[int] = Field(None, ge=0)
    data_export_limit: Optional[int] = Field(None, ge=0)
    ai_queries_limit: Optional[int] = Field(None, ge=0)
    features: Optional[str] = None
    notes: Optional[str] = None


class Subscription(SubscriptionBase):
    """Schema for Subscription response."""
    id: int
    user_id: int
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    stripe_price_id: Optional[str] = None
    status: str
    cancel_at_period_end: bool = False
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    api_rate_limit: int = 1000
    data_export_limit: int = 100
    ai_queries_limit: int = 50
    features: Optional[str] = None
    stripe_webhook_payload: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionWithUser(Subscription):
    """Schema for Subscription with user details."""
    user_email: Optional[str] = None
    user_full_name: Optional[str] = None
    user_organization: Optional[str] = None


class SubscriptionHistoryBase(BaseModel):
    """Base SubscriptionHistory schema."""
    subscription_id: int = Field(..., gt=0)
    event_type: str = Field(..., pattern="^(created|updated|canceled|renewed)$")
    new_status: str = Field(..., pattern="^(active|canceled|past_due|trialing)$")


class SubscriptionHistory(SubscriptionHistoryBase):
    """Schema for SubscriptionHistory response."""
    id: int
    previous_tier: Optional[str] = None
    new_tier: Optional[str] = None
    previous_status: Optional[str] = None
    stripe_event_id: str
    stripe_event_type: str
    event_timestamp: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionUsage(BaseModel):
    """Schema for subscription usage statistics."""
    api_calls_this_month: int = 0
    api_calls_total: int = 0
    data_exports_this_month: int = 0
    data_exports_total: int = 0
    ai_queries_this_month: int = 0
    ai_queries_total: int = 0
    period_start: datetime
    period_end: datetime


class SubscriptionTier(BaseModel):
    """Schema for subscription tier information."""
    tier: str
    name: str
    price: float
    currency: str
    billing_interval: str
    features: List[str]
    api_rate_limit: int
    data_export_limit: int
    ai_queries_limit: int
    is_popular: bool = False


class StripeWebhookEvent(BaseModel):
    """Schema for Stripe webhook events."""
    event_id: str
    event_type: str
    data: dict
    created: datetime = Field(default_factory=datetime.utcnow)


class CheckoutSessionCreate(BaseModel):
    """Schema for creating a Stripe checkout session."""
    tier: str = Field(..., pattern="^(pro|enterprise)$")
    success_url: str = Field(..., max_length=500)
    cancel_url: str = Field(..., max_length=500)
    customer_email: str = Field(..., max_length=255)
    customer_name: str = Field(..., max_length=255)


class CheckoutSessionResponse(BaseModel):
    """Schema for checkout session response."""
    session_id: str
    checkout_url: str
    tier: str
    price: float
    currency: str
