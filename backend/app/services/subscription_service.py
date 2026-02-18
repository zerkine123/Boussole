# ============================================
# Boussole - Subscription Service
# ============================================

"""
Subscription service for managing user subscriptions and Stripe integration.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
import logging
import stripe
from datetime import datetime, timedelta

from app.models.subscription import Subscription, SubscriptionHistory
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    Subscription,
    SubscriptionWithUser,
    SubscriptionUsage,
    SubscriptionTier,
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    StripeWebhookEvent,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_API_KEY if hasattr(settings, 'STRIPE_API_KEY') else None


class SubscriptionService:
    """
    Service layer for subscription operations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_subscription(self, user_id: int) -> Optional[Subscription]:
        """
        Get user's active subscription.
        
        Args:
            user_id: User ID
            
        Returns:
            Active subscription or None
        """
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .where(Subscription.status == "active")
            .order_by(Subscription.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def create_subscription(
        self,
        subscription_data: SubscriptionCreate
    ) -> Subscription:
        """
        Create a new subscription (admin only).
        
        Args:
            subscription_data: Subscription data
            
        Returns:
            Created subscription
        """
        db_subscription = Subscription(**subscription_data.model_dump())
        self.db.add(db_subscription)
        await self.db.commit()
        await self.db.refresh(db_subscription)
        
        # Create history record
        await self._create_history_record(
            db_subscription.id,
            "created",
            None,
            db_subscription.tier,
            db_subscription.status,
        )
        
        logger.info(f"Created subscription for user {subscription_data.user_id}")
        return db_subscription
    
    async def update_subscription(
        self,
        subscription_id: int,
        update_data: SubscriptionUpdate
    ) -> Optional[Subscription]:
        """
        Update an existing subscription.
        
        Args:
            subscription_id: Subscription ID
            update_data: Updated subscription data
            
        Returns:
            Updated subscription or None
        """
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return None
        
        # Store old values for history
        old_tier = subscription.tier
        old_status = subscription.status
        
        # Update subscription
        update_dict = update_data.model_dump(exclude_unset=True)
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(**update_dict)
        )
        await self.db.commit()
        await self.db.refresh(subscription)
        
        # Create history record
        new_tier = update_dict.get("tier", old_tier)
        new_status = update_dict.get("status", old_status)
        
        await self._create_history_record(
            subscription_id,
            "updated",
            old_tier,
            new_tier,
            old_status,
            new_status,
        )
        
        logger.info(f"Updated subscription {subscription_id}")
        return subscription
    
    async def cancel_subscription(self, subscription_id: int) -> bool:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            True if successful, False otherwise
        """
        result = await self.db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return False
        
        # Cancel in Stripe if applicable
        if subscription.stripe_subscription_id:
            try:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
            except Exception as e:
                logger.error(f"Failed to cancel Stripe subscription: {e}")
        
        # Update database
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(status="canceled")
        )
        await self.db.commit()
        
        # Create history record
        await self._create_history_record(
            subscription_id,
            "canceled",
            subscription.tier,
            None,
            subscription.status,
            "canceled",
        )
        
        logger.info(f"Canceled subscription {subscription_id}")
        return True
    
    async def get_subscription_usage(self, user_id: int) -> SubscriptionUsage:
        """
        Get subscription usage statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            Usage statistics
        """
        # Placeholder implementation
        # In production, track actual API calls, exports, and AI queries
        return SubscriptionUsage(
            api_calls_this_month=0,
            api_calls_total=0,
            data_exports_this_month=0,
            data_exports_total=0,
            ai_queries_this_month=0,
            ai_queries_total=0,
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
        )
    
    async def get_available_tiers(self) -> List[SubscriptionTier]:
        """
        Get available subscription tiers.
        
        Returns:
            List of subscription tiers
        """
        # Define subscription tiers
        tiers = [
            SubscriptionTier(
                tier="free",
                name="Free",
                price=0.0,
                currency="DZD",
                billing_interval="month",
                features=[
                    "Basic dashboard access",
                    "Limited data exports",
                    "5 AI queries per day",
                ],
                api_rate_limit=100,
                data_export_limit=100,
                ai_queries_limit=50,
                is_popular=True,
            ),
            SubscriptionTier(
                tier="pro",
                name="Pro",
                price=2000.0,
                currency="DZD",
                billing_interval="month",
                features=[
                    "Full dashboard access",
                    "Unlimited data exports",
                    "100 AI queries per day",
                    "Priority support",
                    "Advanced analytics",
                ],
                api_rate_limit=10000,
                data_export_limit=10000,
                ai_queries_limit=5000,
                is_popular=False,
            ),
            SubscriptionTier(
                tier="enterprise",
                name="Enterprise",
                price=10000.0,
                currency="DZD",
                billing_interval="month",
                features=[
                    "Everything in Pro",
                    "Custom integrations",
                    "Dedicated support",
                    "SLA guarantee",
                    "White-labeling option",
                ],
                api_rate_limit=100000,
                data_export_limit=100000,
                ai_queries_limit=50000,
                is_popular=False,
            ),
        ]
        
        return tiers
    
    async def create_checkout_session(
        self,
        user_id: int,
        checkout_data: CheckoutSessionCreate
    ) -> CheckoutSessionResponse:
        """
        Create a Stripe checkout session.
        
        Args:
            user_id: User ID
            checkout_data: Checkout session data
            
        Returns:
            Checkout session response
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Get tier details
        tiers = await self.get_available_tiers()
        tier = next((t for t in tiers if t.tier == checkout_data.tier), None)
        
        if not tier:
            raise ValueError(f"Invalid tier: {checkout_data.tier}")
        
        # Create Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": tier.currency,
                        "product_data": {
                            "name": f"Boussole {tier.name} Subscription",
                            "description": f"{tier.name} subscription for Boussole",
                        },
                        "unit_amount": int(tier.price * 100),  # Convert to cents
                    },
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=checkout_data.success_url,
                cancel_url=checkout_data.cancel_url,
                customer_email=user.email,
                customer_name=user.full_name,
                metadata={
                    "user_id": str(user_id),
                    "tier": tier.tier,
                },
            )
        except Exception as e:
            logger.error(f"Failed to create Stripe checkout session: {e}")
            raise
        
        # Create or update subscription record
        subscription = Subscription(
            user_id=user_id,
            tier=tier.tier,
            price=tier.price,
            currency=tier.currency,
            billing_interval=tier.billing_interval,
            status="active",
            stripe_checkout_session_id=checkout_session.id,
        )
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        
        return CheckoutSessionResponse(
            session_id=checkout_session.id,
            checkout_url=checkout_session.url,
            tier=tier.tier,
            price=tier.price,
            currency=tier.currency,
        )
    
    async def handle_stripe_webhook(self, event_data: StripeWebhookEvent) -> bool:
        """
        Handle Stripe webhook events.
        
        Args:
            event_data: Stripe webhook event data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify webhook signature
            # In production, verify webhook signature using Stripe secret
            
            # Handle different event types
            if event_data.event_type == "checkout.session.completed":
                # Update subscription to active
                await self._handle_checkout_completed(event_data)
            
            elif event_data.event_type == "invoice.payment_succeeded":
                # Payment succeeded
                await self._handle_payment_succeeded(event_data)
            
            elif event_data.event_type == "customer.subscription.deleted":
                # Subscription canceled
                await self._handle_subscription_deleted(event_data)
            
            logger.info(f"Processed Stripe webhook: {event_data.event_type}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to handle Stripe webhook: {e}")
            return False
    
    async def _handle_checkout_completed(self, event_data: StripeWebhookEvent):
        """Handle checkout.session.completed event."""
        # Find subscription by checkout session ID
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.stripe_checkout_session_id == event_data.data.get("session_id"))
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # Update subscription with Stripe subscription ID
            stripe_subscription_id = event_data.data.get("subscription")
            await self.db.execute(
                update(Subscription)
                .where(Subscription.id == subscription.id)
                .values(stripe_subscription_id=stripe_subscription_id, status="active")
            )
            await self.db.commit()
    
    async def _handle_payment_succeeded(self, event_data: StripeWebhookEvent):
        """Handle invoice.payment_succeeded event."""
        # Update subscription period end
        # This is a simplified implementation
        pass
    
    async def _handle_subscription_deleted(self, event_data: StripeWebhookEvent):
        """Handle customer.subscription.deleted event."""
        # Find subscription by Stripe customer ID
        stripe_customer_id = event_data.data.get("customer")
        
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.stripe_customer_id == stripe_customer_id)
            .where(Subscription.status == "active")
        )
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # Cancel subscription
            await self.cancel_subscription(subscription.id)
    
    async def _create_history_record(
        self,
        subscription_id: int,
        event_type: str,
        previous_tier: Optional[str],
        new_tier: Optional[str],
        previous_status: Optional[str],
        new_status: Optional[str],
        stripe_event_id: Optional[str] = None,
        stripe_event_type: Optional[str] = None,
    ):
        """Create a subscription history record."""
        history = SubscriptionHistory(
            subscription_id=subscription_id,
            event_type=event_type,
            previous_tier=previous_tier,
            new_tier=new_tier,
            previous_status=previous_status,
            new_status=new_status,
            stripe_event_id=stripe_event_id,
            stripe_event_type=stripe_event_type,
            event_timestamp=datetime.utcnow(),
        )
        self.db.add(history)
        await self.db.commit()
