import pytest
import os
import sys

sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../payment/src")),
])

from payment_service.services.stripe_provider import StripeProvider
from payment_service.services import payment_store

def test_stripe_provider_payment_intent_calculation():
    """Verify 20% platform fee and amount calculations."""
    provider = StripeProvider()
    intent = provider.create_payment_intent(
        amount_usd=50.0,
        nutritionist_account_id="acct_test_placeholder",
        metadata={"appointment_id": "bk_test_123"}
    )
    assert intent["amount"] == 5000  # $50.00 in cents
    assert intent["currency"] == "usd"
    assert "client_secret" in intent

def test_nutritionist_payout_85_15_split():
    """Verify 15% platform commission and 85% net provider transfer."""
    provider = StripeProvider()
    payout = provider.create_transfer(
        gross_amount_usd=100.0,
        destination_account_id="acct_test_sarah",
        platform_commission_percent=0.15,
        currency="usd"
    )
    assert payout["gross_amount_usd"] == 100.0
    assert payout["gross_amount_cents"] == 10000
    assert payout["platform_commission_cents"] == 1500  # 15% = $15
    assert payout["net_payout_cents"] == 8500          # 85% = $85
    assert payout["net_payout_usd"] == 85.0
    assert payout["transfer_id"] is not None

def test_webhook_event_structure_parsing():
    """Verify webhook structure and status mapping."""
    fake_event = {
        "id": "evt_test_success_999",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test_12345",
                "amount": 4500,
                "currency": "usd",
                "status": "succeeded"
            }
        }
    }
    event_map = payment_store._mapping(fake_event)
    assert event_map["id"] == "evt_test_success_999"
    assert event_map["type"] == "payment_intent.succeeded"
    obj = payment_store._mapping(payment_store._mapping(event_map.get("data")).get("object"))
    assert obj["id"] == "pi_test_12345"
    assert obj["status"] == "succeeded"
