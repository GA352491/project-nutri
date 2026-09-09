"""
Stripe integration for NutriPlan Payment Service.

Uses the official stripe-python SDK. Reads STRIPE_SECRET_KEY from the environment.
For local development the key is loaded from the root project .env file automatically.
"""
import os
from pathlib import Path
from typing import Optional
import stripe

# Load root .env so STRIPE_SECRET_KEY is available regardless of how the service is started
_root_env = Path(__file__).parents[5] / ".env"
if _root_env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_root_env, override=False)
    except ImportError:
        pass  # python-dotenv not available — rely on shell environment

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
PLATFORM_FEE_PERCENT = float(os.getenv("PLATFORM_FEE_PERCENT", "0.20"))  # 20%

stripe.api_key = STRIPE_SECRET_KEY


class StripeProvider:
    """
    Handles interactions with the Stripe API.
    Manages Stripe Connect accounts for nutritionists and payment intents for bookings.
    """

    # ---------------------------------------------------------------------------
    # Stripe Connect — nutritionist onboarding
    # ---------------------------------------------------------------------------

    def create_connect_account(self, nutritionist_id: str, email: str = "") -> str:
        """
        Creates an Express connected account for a nutritionist.
        Returns the Stripe account ID (acct_...).
        """
        params: dict = {
            "type": "express",
            "capabilities": {
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
            "metadata": {"nutritionist_id": nutritionist_id},
        }
        if email:
            params["email"] = email

        account = stripe.Account.create(**params)
        return account.id

    def generate_account_link(self, account_id: str, refresh_url: str = "", return_url: str = "") -> str:
        """
        Generates the hosted onboarding URL where the nutritionist enters bank details.
        """
        from nutriplan_shared.service_registry import FRONTEND_URL as _REG_FRONTEND_URL
        base = os.getenv("FRONTEND_URL", _REG_FRONTEND_URL)
        link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url or f"{base}/expert/onboard?refresh=1",
            return_url=return_url or f"{base}/expert/onboard?success=1",
            type="account_onboarding",
        )
        return link.url

    # ---------------------------------------------------------------------------
    # Payment Intents — booking checkout
    # ---------------------------------------------------------------------------

    def create_payment_intent(
        self,
        amount_usd: float,
        nutritionist_account_id: str,
        metadata: dict | None = None,
    ) -> dict:
        """
        Creates a PaymentIntent for a booking.
        When a real Stripe Connect account is provided (acct_ prefix, not a placeholder),
        uses a destination charge so Stripe routes (1 - PLATFORM_FEE_PERCENT) directly
        to the nutritionist's connected account.
        In local dev (placeholder account ID), creates a plain PaymentIntent.
        """
        amount_cents = int(round(amount_usd * 100))
        fee_cents = int(round(amount_cents * PLATFORM_FEE_PERCENT))

        # Detect a real Stripe Connect account vs. dev placeholder
        is_real_connect_account = (
            nutritionist_account_id
            and nutritionist_account_id.startswith("acct_")
            and "placeholder" not in nutritionist_account_id
            and "test_" not in nutritionist_account_id
        )

        params: dict = {
            "amount": amount_cents,
            "currency": "usd",
            "payment_method_types": ["card"],
            "metadata": metadata or {},
        }
        if is_real_connect_account:
            params["application_fee_amount"] = fee_cents
            params["transfer_data"] = {"destination": nutritionist_account_id}

        intent = stripe.PaymentIntent.create(**params)
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": intent.amount,
            "application_fee_amount": fee_cents if is_real_connect_account else 0,
            "transfer_data": {"destination": nutritionist_account_id} if is_real_connect_account else None,
            "currency": intent.currency,
            "connect_mode": "platform_split" if is_real_connect_account else "direct_dev",
        }

    def create_setup_intent(self, customer_id: Optional[str] = None, metadata: dict | None = None) -> dict:
        """
        Creates a SetupIntent for subscription free trials (card pre-authorization without upfront charge).
        """
        params: dict = {
            "payment_method_types": ["card"],
            "metadata": metadata or {},
        }
        if customer_id:
            params["customer"] = customer_id
        
        intent = stripe.SetupIntent.create(**params)
        return {
            "client_secret": intent.client_secret,
            "setup_intent_id": intent.id,
            "status": intent.status
        }

    def create_checkout_session(
        self,
        tier: str,
        user_id: Optional[str] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        metadata: dict | None = None,
    ) -> dict:
        """
        Creates an official hosted Stripe Checkout Session for recurring subscriptions or one-time trials.
        Returns the hosted checkout URL where user securely enters their credit card or UPI details on Stripe.
        """
        unit_amount = 49900 if tier.lower() == "pro" else (89900 if tier.lower() == "family" else 0)
        plan_name = "NutriPlan Pro Clinical AI" if tier.lower() == "pro" else ("NutriPlan Family Care" if tier.lower() == "family" else "NutriPlan Basic")

        meta = {"tier": tier, "user_id": user_id or "usr_mobile_patient", **(metadata or {})}

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": plan_name,
                            "description": f"{plan_name} membership with AI clinical guardrails & grocery sync",
                        },
                        "unit_amount": unit_amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url or "https://nutriplan.app/checkout/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url or "https://nutriplan.app/checkout/cancel",
            metadata=meta,
        )

        return {
            "session_id": session.id,
            "checkout_url": session.url,
            "status": session.status,
        }

    def create_transfer(
        self,
        gross_amount_usd: float,
        destination_account_id: str,
        platform_commission_percent: float = 0.15,
        currency: str = "usd",
        description: str = "Telehealth Consultation Net Payout",
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Transfers net earnings (1 - commission) directly to a nutritionist's connected Stripe account.
        """
        gross_cents = int(round(gross_amount_usd * 100))
        commission_cents = int(round(gross_cents * platform_commission_percent))
        net_payout_cents = gross_cents - commission_cents

        is_real_connect = (
            destination_account_id
            and destination_account_id.startswith("acct_")
            and "placeholder" not in destination_account_id
            and "test_" not in destination_account_id
        )

        if is_real_connect:
            transfer = stripe.Transfer.create(
                amount=net_payout_cents,
                currency=currency,
                destination=destination_account_id,
                description=description,
                metadata={
                    **(metadata or {}),
                    "gross_amount_usd": str(gross_amount_usd),
                    "platform_commission_percent": str(platform_commission_percent),
                }
            )
            transfer_id = transfer.id
        else:
            transfer_id = f"tr_mock_{destination_account_id[:8]}_{net_payout_cents}"

        return {
            "transfer_id": transfer_id,
            "destination_account_id": destination_account_id,
            "gross_amount_usd": gross_amount_usd,
            "gross_amount_cents": gross_cents,
            "platform_commission_cents": commission_cents,
            "net_payout_cents": net_payout_cents,
            "net_payout_usd": round(net_payout_cents / 100.0, 2),
            "currency": currency,
            "status": "paid" if is_real_connect else "simulated_success"
        }

    # ---------------------------------------------------------------------------
    # Webhooks
    # ---------------------------------------------------------------------------

    def construct_webhook_event(self, payload: bytes, sig_header: str):
        """
        Validates the Stripe-Signature header and returns the parsed event.
        Raises stripe.error.SignatureVerificationError on failure.
        """
        return stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)


stripe_provider = StripeProvider()
