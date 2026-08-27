import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../recipe/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")))

def test_recipe_service_health():
    from recipe_service.main import app
    client = TestClient(app, raise_server_exceptions=False)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_recipe_create_validation():
    from recipe_service.main import app
    client = TestClient(app, raise_server_exceptions=False)
    # Missing required title should return 422
    invalid_payload = {
        "cuisine": "Indian"
    }
    res = client.post("/api/v1/recipes/", json=invalid_payload)
    assert res.status_code == 422
