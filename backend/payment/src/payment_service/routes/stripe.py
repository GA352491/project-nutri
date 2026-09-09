from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional
import stripe

from ..services.stripe_provider import stripe_provider
from ..services import payment_store
from ..schemas.payment_schemas import (
    ConnectInitRequest,
    BookingPaymentRequest,
    SetupIntentRequest,
    HostedCheckoutRequest,
    PayoutTransferRequest,
)

router = APIRouter()


@router.post("/payout/transfer")
async def process_nutritionist_payout(req: PayoutTransferRequest):
    """
    Transfers net earnings to a nutritionist's Stripe Connect account.
    Deducts the platform commission (default 15%) and sends remaining 85% to provider.
    """
    try:
        transfer = stripe_provider.create_transfer(
            gross_amount_usd=req.gross_amount_usd,
            destination_account_id=req.destination_account_id,
            platform_commission_percent=req.platform_commission_percent or 0.15,
            currency=req.currency or "usd",
            description=req.description or "Telehealth Consultation Net Payout",
            metadata=req.metadata,
        )
        return {
            "status": "success",
            "payout": transfer
        }
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe Transfer error: {e.user_message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payout processing error: {str(e)}")


@router.post("/connect/init")
async def init_stripe_connect(req: ConnectInitRequest):
    """
    Called after a nutritionist completes the marketplace onboarding form.
    Initializes their Stripe Connect account so they can receive payouts.
    Returns the hosted Stripe onboarding URL.
    """
    try:
        account_id = stripe_provider.create_connect_account(
            nutritionist_id=req.nutritionist_id,
            email=req.email or "",
        )
        onboarding_url = stripe_provider.generate_account_link(account_id)
        record = await payment_store.record_connect_account(
            nutritionist_id=req.nutritionist_id,
            stripe_account_id=account_id,
            email=req.email or "",
        )
        return {
            "status": "success",
            "stripe_account_id": account_id,
            "onboarding_url": onboarding_url,
            "connect_account_id": str(record.id) if record else None,
        }
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {e.user_message}")


@router.post("/checkout/booking")
async def create_booking_payment(req: BookingPaymentRequest):
    """
    Creates a PaymentIntent for a booking, grocery hold, or subscription charge.
    Automatically splits the payment (platform keeps 20%, nutritionist receives 80%)
    when a real Connect account is provided.
    Persists a Payment ledger row owned by this service.
    """
    try:
        metadata = {
            "appointment_id": req.appointment_id,
            **(req.metadata or {}),
        }
        if req.user_id:
            metadata.setdefault("user_id", req.user_id)

        intent = stripe_provider.create_payment_intent(
            amount_usd=req.amount_usd,
            nutritionist_account_id=req.nutritionist_account_id,
            metadata=metadata,
        )
        record = await payment_store.record_payment_intent(
            amount_cents=intent["amount"],
            currency=intent.get("currency") or "usd",
            platform_fee_cents=intent.get("application_fee_amount") or 0,
            provider_object_id=intent["payment_intent_id"],
            destination_account_id=req.nutritionist_account_id,
            reference_id=req.appointment_id,
            metadata=metadata,
            user_id=req.user_id,
        )
        return {
            "status": "success",
            "client_secret": intent["client_secret"],
            "payment_intent_id": intent["payment_intent_id"],
            "platform_fee_cents": intent["application_fee_amount"],
            "total_amount_cents": intent["amount"],
            "payment_id": str(record.id) if record else None,
        }
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {e.user_message}")


@router.post("/checkout/setup-intent")
async def create_setup_intent(req: SetupIntentRequest):
    """
    Creates a SetupIntent for subscription free trials (card pre-authorization without upfront charge).
    Returns the `client_secret` for Stripe Elements on the frontend.
    """
    try:
        metadata = {"tier": req.tier, "user_id": req.user_id or "usr_patient_01"}
        intent = stripe_provider.create_setup_intent(metadata=metadata)
        record = await payment_store.record_setup_intent(
            provider_object_id=intent["setup_intent_id"],
            metadata=metadata,
            user_id=req.user_id,
        )
        return {
            "status": "success",
            "client_secret": intent["client_secret"],
            "setup_intent_id": intent["setup_intent_id"],
            "payment_id": str(record.id) if record else None,
        }
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe error: {e.user_message}")


@router.post("/checkout/session")
async def create_checkout_session(req: HostedCheckoutRequest):
    """
    Creates an official Stripe Checkout Session for recurring plan subscriptions.
    Returns the real Stripe-hosted checkout URL for web and mobile browsers.
    """
    try:
        session_data = stripe_provider.create_checkout_session(
            tier=req.tier,
            user_id=req.user_id,
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            metadata=req.metadata,
        )
        return {
            "status": "success",
            "checkout_url": session_data["checkout_url"],
            "session_id": session_data["session_id"],
        }
    except stripe.StripeError as e:
        raise HTTPException(status_code=502, detail=f"Stripe Checkout error: {e.user_message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout initialization error: {str(e)}")


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature"),
):
    """
    Receives and processes Stripe webhook events.
    Secured via Stripe-Signature header verification.
    Updates Payment and ConnectAccount rows; duplicates are ignored.
    """
    payload = await request.body()

    try:
        event = stripe_provider.construct_webhook_event(
            payload=payload,
            sig_header=stripe_signature or "",
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")

    result = await payment_store.apply_webhook_event(event)
    return result
