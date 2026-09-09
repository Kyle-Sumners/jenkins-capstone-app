import pytest
from app import app

@pytest.fixture
def client():
  return app.test_client()

def test_home(client):
  response = client.get("/")
  assert response.status_code == 200
  assert b"Capstone Application" in response.data

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

def test_health_version(client, monkeypatch):
  monkeypatch.setenv("VERSION", "9.9.9-test")
  response = client.get("/health")
  assert response.get_json()["version"] == "9.9.9-test"

def test_health_version_default(client, monkeypatch):
  monkeypatch.delenv("VERSION", raising=False)
  response = client.get("/health")
  assert response.get_json()["version"] == "0.0.0"

def test_health_uptime(client):
  response = client.get("/health")
  uptime = response.get_json()["uptime"]
  assert isinstance(uptime, int)
  assert uptime >= 0

def test_home_shows_uptime(client):
  response = client.get("/")
  assert b"Downtime" in response.data