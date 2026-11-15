from fastapi.testclient import TestClient

from app.main import app


def test_health_and_public_settings():
    with TestClient(app) as client:
        assert client.get("/api/v1/health").json() == {"status": "ok"}
        settings = client.get("/api/v1/site-settings").json()
        assert settings["business_name"] == "Jewel Essence Hair Studio"
        assert "415 Wick Lane" in settings["address"]


def test_admin_requires_authentication():
    with TestClient(app) as client:
        assert client.get("/api/v1/admin/pricelist/categories").status_code == 401
