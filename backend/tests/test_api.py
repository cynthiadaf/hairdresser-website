from fastapi.testclient import TestClient

from app.main import app


def test_health_and_gallery_api():
    with TestClient(app) as client:
        assert client.get("/api/v1/health").json() == {"status": "ok"}
        assert client.get("/api/v1/gallery").status_code == 200


def test_obsolete_database_backed_routes_are_removed():
    with TestClient(app) as client:
        for path in ("/api/v1/site-settings", "/api/v1/pricelist", "/api/v1/auth/me"):
            assert client.get(path).status_code == 404
