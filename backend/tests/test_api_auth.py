import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../auth/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")))

def test_auth_health_check():
    from auth_service.main import app
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_auth_login_validation():
    from auth_service.main import app
    client = TestClient(app, raise_server_exceptions=False)
    # Missing password should trigger 422 Unprocessable Entity
    login_payload = {
        "email": "user@example.com"
    }
    res = client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 422
