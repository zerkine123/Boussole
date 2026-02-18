# ============================================
# Boussole - Subscription Model
# ============================================

"""
Subscription model for user subscription tiers and billing.
Supports Stripe integration for payment processing.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Subscription(Base):
    """
    Subscription model for user subscription tiers.
    """
    
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Subscription tier
    tier = Column(String(50), nullable=False)  # free, pro, enterprise
    stripe_customer_id = Column(String(255), index=True)  # Stripe customer ID
    stripe_subscription_id = Column(String(255), index=True)  # Stripe subscription ID
    stripe_price_id = Column(String(255))  # Stripe price ID
    
    # Subscription status
    status = Column(String(50), nullable=False, default="active")  # active, canceled, past_due, trialing
    cancel_at_period_end = Column(Boolean, default=False)  # Auto-renew or cancel at period end
    
    # Billing period
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    trial_start = Column(DateTime)
    trial_end = Column(DateTime)
    
    # Pricing
    price = Column(Float, nullable=False)  # Monthly price in DZD
    currency = Column(String(3), default="DZD")
    billing_interval = Column(String(20), default="month")  # month, year
    
    # Features (JSON)
    features = Column(Text)  # JSON string of enabled features
    api_rate_limit = Column(Integer, default=1000)  # API calls per day
    data_export_limit = Column(Integer, default=100)  # Export rows per month
    ai_queries_limit = Column(Integer, default=50)  # AI queries per day
    
    # Metadata
    stripe_webhook_payload = Column(Text)  # Store latest webhook payload
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    history = relationship("SubscriptionHistory", back_populates="subscription", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, tier={self.tier})>"


class SubscriptionHistory(Base):
    """
    SubscriptionHistory model for tracking subscription changes.
    """
    
    __tablename__ = "subscription_history"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    
    # Change details
    event_type = Column(String(50), nullable=False)  # created, updated, canceled, renewed
    previous_tier = Column(String(50))
    new_tier = Column(String(50))
    previous_status = Column(String(50))
    new_status = Column(String(50))
    
    # Stripe event data
    stripe_event_id = Column(String(255), unique=True, index=True)
    stripe_event_type = Column(String(100))  # customer.subscription.created, etc.
    
    # Timestamps
    event_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="history")
    
    def __repr__(self):
        return f"<SubscriptionHistory(id={self.id}, event_type={self.event_type})>"
