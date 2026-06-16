"""Billing and subscription management."""

import stripe
from database import SessionLocal
from models import Tenant
from datetime import datetime, timedelta
from config import settings

stripe.api_key = settings.stripe_api_key

PRICING_TIERS = {
    "starter": {
        "price_usd": 299,
        "max_employees": 50,
        "max_seats": 1,
        "features": ["basic_threat_detection", "daily_reports"]
    },
    "professional": {
        "price_usd": 999,
        "max_employees": 500,
        "max_seats": 5,
        "features": ["advanced_ml", "hourly_reports", "api_access", "integrations"]
    },
    "enterprise": {
        "price_usd": "custom",
        "max_employees": float('inf'),
        "max_seats": float('inf'),
        "features": ["everything", "dedicated_support", "sso", "custom_integrations"]
    }
}


def create_customer(tenant: Tenant, email: str, name: str) -> str:
    """Create Stripe customer for tenant."""
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"tenant_id": str(tenant.id)}
        )
        return customer.id
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to create Stripe customer: {str(e)}")


def create_subscription(tenant: Tenant, tier: str) -> dict:
    """Create subscription for tenant."""
    db = SessionLocal()
    try:
        if not tenant.stripe_customer_id:
            raise Exception("Customer not created")

        # In production, use actual Stripe price IDs
        price_map = {
            "starter": "price_starter_monthly",
            "professional": "price_professional_monthly",
            "enterprise": "price_enterprise_custom"
        }

        subscription = stripe.Subscription.create(
            customer=tenant.stripe_customer_id,
            items=[{"price": price_map.get(tier, price_map["starter"])}],
            metadata={"tenant_id": str(tenant.id), "tier": tier}
        )

        # Update tenant
        tenant.subscription_tier = tier
        db.commit()

        return {
            "subscription_id": subscription.id,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "tier": tier
        }
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to create subscription: {str(e)}")
    finally:
        db.close()


def get_subscription_status(tenant: Tenant) -> dict:
    """Get subscription status."""
    if not tenant.stripe_customer_id:
        return {
            "status": "no_subscription",
            "tier": tenant.subscription_tier
        }

    try:
        subscriptions = stripe.Subscription.list(
            customer=tenant.stripe_customer_id,
            limit=1
        )
        if subscriptions.data:
            sub = subscriptions.data[0]
            return {
                "status": sub.status,
                "tier": tenant.subscription_tier,
                "current_period_end": datetime.fromtimestamp(sub.current_period_end),
                "cancel_at_period_end": sub.cancel_at_period_end
            }
    except stripe.error.StripeError:
        pass

    return {"status": "unknown", "tier": tenant.subscription_tier}


def track_usage(tenant: Tenant, metric: str, amount: int):
    """Track usage for metering (per-employee monitoring)."""
    # Implementation for usage-based billing
    pass


def handle_webhook(event_type: str, event_data: dict):
    """Handle Stripe webhook events."""
    if event_type == "customer.subscription.updated":
        # Update subscription status
        pass
    elif event_type == "customer.subscription.deleted":
        # Handle cancellation
        pass
    elif event_type == "invoice.payment_failed":
        # Handle payment failure
        pass
