import pytest
from app import app

@pytest.fixture
def client():
  return app.test_client()

def test_home(client):
  response = client.get("/")
  assert response.status_code == 200
  assert b"Hello, World!" in response.data

def test_health_healthy(client, monkeypatch):
  monkeypatch.setenv("DB_STATUS", "up")
  response = client.get("/health")
  assert response.status_code == 200
  assert response.get_json()["status"] == "healthy"

def test_health_unhealthy(client, monkeypatch):
  monkeypatch.setenv("DB_STATUS", "down")
  response = client.get("/health")
  assert response.status_code == 503
  assert response.get_json()["status"] == "unhealthy"
