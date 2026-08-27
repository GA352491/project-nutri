import pytest
import asyncio
import sys
import os

sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../delivery/src")),
])

from delivery_service.temporal_workers.grocery_delivery_worker import (
    reserve_grocery_inventory,
    authorize_stripe_hold,
    dispatch_delivery_rider,
    compensate_cancel_stripe_hold,
)

def test_grocery_delivery_saga_forward_flow():
    """Verify quick commerce saga forward path."""
    order_id = "ORD-TEST-123"
    items = ["Organic Paneer", "Fresh Spinach", "Toor Dal"]
    partner = "Blinkit"
    amount_usd = 18.50
    address = "124, Green Park, Indiranagar, Bengaluru"

    # Step 1: Reserve inventory
    inv = asyncio.run(reserve_grocery_inventory(order_id, items, partner))
    assert inv["status"] == "RESERVED"
    assert inv["partner"] == "Blinkit"
    assert inv["item_count"] == 3

    # Step 2: Authorize Stripe hold
    hold_pi = asyncio.run(authorize_stripe_hold(order_id, amount_usd))
    assert hold_pi is not None
    assert "ORD-TEST" in hold_pi or "pi_" in hold_pi

    # Step 3: Dispatch rider
    rider = asyncio.run(dispatch_delivery_rider(order_id, address, partner))
    assert rider["status"] == "RIDER_ASSIGNED"
    assert rider["eta_minutes"] <= 15

def test_grocery_delivery_saga_compensation_flow():
    """Verify compensation rollback cancels auth hold without throwing."""
    order_id = "ORD-CANCEL-999"
    pi_id = "pi_hold_cancel_123"
    reason = "Out of stock on organic spinach"

    # Activity runs cleanly without error
    asyncio.run(compensate_cancel_stripe_hold(order_id, pi_id, reason))
