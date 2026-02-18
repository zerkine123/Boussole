"""
Stripe Webhook Endpoints

This module handles Stripe webhook events for subscription management.
It processes events like:
- checkout.session.completed
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted
- invoice.payment_succeeded
- invoice.payment_failed

Security:
- Validates Stripe webhook signatures
- Verifies event authenticity
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from sqlalchemy.orm import Session
from stripe import Webhook, StripeError

from app.db.session import get_db
from app.services.subscription_service import SubscriptionService
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stripe", tags=["stripe"])


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    stripe_signature: str = Header(None, alias="Stripe-Signature")
):
    """
    Handle incoming Stripe webhook events.
    
    This endpoint:
    1. Validates the Stripe signature
    2. Parses the event payload
    3. Processes the event based on type
    4. Updates the database accordingly
    
    Args:
        request: The incoming HTTP request
        background_tasks: FastAPI background tasks
        stripe_signature: The Stripe signature header for validation
        
    Returns:
        Success response
        
    Raises:
        HTTPException: If signature validation fails or processing errors occur
    """
    # Get the raw body
    payload = await request.body()
    payload_str = payload.decode('utf-8')
    
    try:
        # Verify the webhook signature
        event = Webhook.construct_event(
            payload=payload_str,
            sig_header=stripe_signature,
            secret=settings.stripe_webhook_secret
        )
        
        logger.info(f"Received Stripe webhook event: {event.type}")
        
        # Process the event
        await process_stripe_event(event, background_tasks)
        
        return {"status": "success", "event_type": event.type}
        
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid webhook payload: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except StripeError as e:
        # Invalid signature
        logger.error(f"Invalid webhook signature: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        # Unexpected error
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_stripe_event(event: Dict[str, Any], background_tasks: BackgroundTasks):
    """
    Process a Stripe event based on its type.
    
    Args:
        event: The Stripe event object
        background_tasks: FastAPI background tasks for async processing
    """
    db = next(get_db())
    subscription_service = SubscriptionService(db)
    
    event_type = event['type']
    event_data = event['data']['object']
    
    # Route to appropriate handler
    handlers = {
        'checkout.session.completed': handle_checkout_completed,
        'customer.subscription.created': handle_subscription_created,
        'customer.subscription.updated': handle_subscription_updated,
        'customer.subscription.deleted': handle_subscription_deleted,
        'invoice.payment_succeeded': handle_payment_succeeded,
        'invoice.payment_failed': handle_payment_failed,
        'customer.subscription.trial_will_end': handle_trial_ending,
    }
    
    handler = handlers.get(event_type)
    if handler:
        try:
            await handler(event_data, db, subscription_service, background_tasks)
            logger.info(f"Successfully processed event: {event_type}")
        except Exception as e:
            logger.error(f"Error processing event {event_type}: {str(e)}")
    else:
        logger.warning(f"Unhandled event type: {event_type}")


async def handle_checkout_completed(
    session_data: Dict[str, Any],
    db: Session,
    subscription_service: SubscriptionService,
    background_tasks: BackgroundTasks
):
    """
    Handle checkout.session.completed event.
    
    This event occurs when a user completes the checkout flow.
    It creates/updates the subscription in the database.
    """
    # Extract relevant data
    customer_id = session_data.get('customer')
    subscription_id = session_data.get('subscription')
    metadata = session_data.get('metadata', {})
    
    user_id = metadata.get('user_id')
    tier_id = metadata.get('tier_id')
    
    if not user_id:
        logger.error("No user_id in checkout session metadata")
        return
    
    # Create or update subscription
    subscription = await subscription_service.create_subscription_from_stripe(
        user_id=int(user_id),
        stripe_customer_id=customer_id,
        stripe_subscription_id=subscription_id,
        tier_id=int(tier_id) if tier_id else None,
        status='active',
    )
    
    logger.info(f"Created subscription {subscription.id} for user {user_id}")


async def handle_subscription_created(
    subscription_data: Dict[str, Any],
    db: Session,
    subscription_service: SubscriptionService,
    background_tasks: BackgroundTasks
):
    """
    Handle customer.subscription.created event.
    
    This event occurs when a new subscription is created.
    """
    stripe_subscription_id = subscription_data.get('id')
    customer_id = subscription_data.get('customer')
    
    # Find subscription by Stripe ID and update status
    subscription = await subscription_service.get_by_stripe_id(stripe_subscription_id)
    if subscription:
        await subscription_service.update_status(
            subscription.id,
            'active'
        )
        logger.info(f"Activated subscription {subscription.id}")


async def handle_subscription_updated(
    subscription_data: Dict[str, Any],
    db: Session,
    subscription_service: SubscriptionService,
    background_tasks: BackgroundTasks
):
    """
    Handle customer.subscription.updated event.
    
    This event occurs when subscription details change.
    It handles:
    - Plan changes (upgrades/downgrades)
    - Status changes (active, past_due, canceled)
    - Quantity changes
    """
    stripe_subscription_id = subscription_data.get('id')
    status = subscription_data.get('status')
    cancel_at_period_end = subscription_data.get('cancel_at_period_end', False)
    
    # Find subscription by Stripe ID
    subscription = await subscription_service.get_by_stripe_id(stripe_subscription_id)
    if not subscription:
        logger.warning(f"Subscription not found for Stripe ID: {stripe_subscription_id}")
        return
    
    # Update status
    new_status = 'active'
    if cancel_at_period_end:
        new_status = 'canceling'
    elif status == 'past_due':
        new_status = 'past_due'
    elif status == 'canceled':
        new_status = 'canceled'
    elif status == 'unpaid':
        new_status = 'unpaid'
    
    await subscription_service.update_status(subscription.id, new_status)
    
    # Update tier if plan changed
    # TODO: Extract tier from plan and update
    
    logger.info(f"Updated subscription {subscription.id} to status: {new_status}")


async def handle_subscription_deleted(
    subscription_data: Dict[str, Any],
    db: Session,
    subscription_service: SubscriptionService,
    background_tasks: BackgroundTasks
):
    """
    Handle customer.subscription.deleted event.
    
    This event occurs when a subscription is canceled and deleted.
    """
    stripe_subscription_id = subscription_data.get('id')
    
    # Find subscription by Stripe ID and mark as canceled
    subscription = await subscription_service.get_by_stripe_id(stripe_subscription_id)
    if subscription:
        await subscription_service.update_status(subscription.id, 'canceled')
        logger.info(f"Canceled subscription {subscription.id}")


async def handle_payment_succeeded(
    invoice_data: Dict[str, Any],
    db: Session,
    subscription_service: SubscriptionService,
    background_tasks: BackgroundTasks
):
    """
    Handle invoice.payment_succeeded event.
    
    This event occurs when a payment is successful.
    It updates usage tracking and extends subscription.
    """
    subscription_id = invoice_data.get('subscription')
    amount_paid = invoice_data.get('amount_paid', 0) / 100  # Convert from cents
    
    # Find subscription and update
    if subscription_id:
        subscription = await subscription_service.get_by_stripe_id(subscription_id)
        if subscription:
            # Update usage tracking
            await subscription_service.record_payment(
                subscription.id,
                amount_paid,
                datetime.utcnow()
            )
            
            # Extend subscription period
            # TODO: Calculate new end date based on billing cycle
            
            logger.info(f"Payment succeeded for subscription {subscription.id}: ${amount_paid}")


async def handle_payment_failed(
    invoice_data: Dict[str, Any],
    db: Session,
    subscription_service: SubscriptionService,
    background_tasks: BackgroundTasks
):
    """
    Handle invoice.payment_failed event.
    
    This event occurs when a payment fails.
    It updates subscription status and may send notifications.
    """
    subscription_id = invoice_data.get('subscription')
    
    # Find subscription and mark as past due
    if subscription_id:
        subscription = await subscription_service.get_by_stripe_id(subscription_id)
        if subscription:
            await subscription_service.update_status(subscription.id, 'past_due')
            
            # TODO: Send payment failed notification to user
            
            logger.warning(f"Payment failed for subscription {subscription.id}")


async def handle_trial_ending(
    subscription_data: Dict[str, Any],
    db: Session,
    subscription_service: SubscriptionService,
    background_tasks: BackgroundTasks
):
    """
    Handle customer.subscription.trial_will_end event.
    
    This event occurs 3 days before a trial ends.
    It can be used to send reminders to users.
    """
    stripe_subscription_id = subscription_data.get('id')
    
    # Find subscription
    subscription = await subscription_service.get_by_stripe_id(stripe_subscription_id)
    if subscription:
        # TODO: Send trial ending notification to user
        
        logger.info(f"Trial ending for subscription {subscription.id}")


@router.get("/tiers")
async def get_subscription_tiers():
    """
    Get available subscription tiers.
    
    Returns:
        List of subscription tiers with pricing and features
    """
    tiers = [
        {
            "id": 1,
            "name": "Free",
            "price": 0,
            "currency": "USD",
            "interval": "month",
            "features": [
                "Basic data access",
                "5 AI queries per day",
                "Standard reports"
            ],
            "limits": {
                "api_calls": 100,
                "ai_queries": 5,
                "data_exports": 10,
                "forecasts": 0
            }
        },
        {
            "id": 2,
            "name": "Pro",
            "price": 29,
            "currency": "USD",
            "interval": "month",
            "features": [
                "Advanced data access",
                "Unlimited AI queries",
                "Custom reports",
                "Prophet forecasts",
                "Priority support"
            ],
            "limits": {
                "api_calls": 1000,
                "ai_queries": -1,  # Unlimited
                "data_exports": 100,
                "forecasts": 50
            }
        },
        {
            "id": 3,
            "name": "Enterprise",
            "price": 99,
            "currency": "USD",
            "interval": "month",
            "features": [
                "Full data access",
                "Unlimited AI queries",
                "White-label reports",
                "Prophet forecasts",
                "Dedicated support",
                "Custom integrations",
                "SLA guarantee"
            ],
            "limits": {
                "api_calls": -1,  # Unlimited
                "ai_queries": -1,  # Unlimited
                "data_exports": -1,  # Unlimited
                "forecasts": -1  # Unlimited
            }
        }
    ]
    
    return {"tiers": tiers}


@router.get("/health")
async def webhook_health():
    """
    Health check endpoint for webhooks.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "stripe-webhooks",
        "timestamp": datetime.utcnow().isoformat()
    }
