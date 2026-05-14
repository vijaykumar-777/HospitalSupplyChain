from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_orders():
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_inventory():
    response = client.get("/api/inventory")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_disaster_active_state():
    response = client.get("/api/disaster/active")
    assert response.status_code == 200
    assert "active" in response.json()
