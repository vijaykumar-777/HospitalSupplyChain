import os
from fastapi.testclient import TestClient

os.environ["ENABLE_SCHEDULER"] = "false"

from backend.main import app

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_orders():
    with TestClient(app) as client:
        response = client.get("/api/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_inventory():
    with TestClient(app) as client:
        response = client.get("/api/inventory")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_disaster_active_state():
    with TestClient(app) as client:
        response = client.get("/api/disaster/active")
    assert response.status_code == 200
    assert "active" in response.json()

def test_disaster_context():
    with TestClient(app) as client:
        response = client.get("/api/disaster/context")
    assert response.status_code == 200
    hospital = response.json()["hospital"]
    assert {"lat", "lng", "city"} <= hospital.keys()
