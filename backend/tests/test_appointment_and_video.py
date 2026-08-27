import pytest
import asyncio
import sys
import os

sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../appointment/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../video/src")),
])

from appointment_service.temporal_workers.booking_worker import (
    charge_stripe,
    provision_jitsi_room,
    send_confirmation_email,
)

def test_appointment_booking_temporal_activities():
    """Verify booking saga activities succeed with valid parameters."""
    appointment_id = "test_bk_999"
    amount_usd = 25.0
    stripe_account_id = "acct_test_sarah"
    nutritionist_name = "Dr. Sarah Jenkins"
    user_id = "usr_patient_1"

    # 1. Test Stripe charge activity (returns real/mock payment intent ID)
    stripe_pi = asyncio.run(charge_stripe(appointment_id, amount_usd, stripe_account_id))
    assert stripe_pi is not None
    assert stripe_pi.startswith("pi_")

    # 2. Test Video Room provision activity
    room_url = asyncio.run(provision_jitsi_room(appointment_id, nutritionist_name))
    assert room_url is not None
    assert "test_bk_999" in room_url

    # 3. Test Email confirmation activity (does not throw)
    asyncio.run(send_confirmation_email(user_id, room_url, appointment_id))
