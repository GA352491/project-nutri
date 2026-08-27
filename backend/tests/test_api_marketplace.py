import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../marketplace/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")))

def test_marketplace_health():
    from marketplace_service.main import app
    client = TestClient(app, raise_server_exceptions=False)
    res = client.get("/health")
    assert res.status_code == 200

def test_marketplace_onboarding_minimum_rate_validation():
    from marketplace_service.main import app
    client = TestClient(app, raise_server_exceptions=False)
    invalid_profile = {
        "name": "Dr. Cheap",
        "bio": "Discount advice",
        "specialties": ["General"],
        "hourly_rate_usd": 15.0,  # Below $20 floor
        "certifications": ["Cert A"]
    }
    res = client.post("/api/v1/marketplace/nutritionists/onboard", json=invalid_profile)
    assert res.status_code == 400
    assert "at least $20" in res.json()["detail"]
