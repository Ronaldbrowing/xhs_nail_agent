"""
Tests for GET /api/verticals endpoint.
"""
import pytest
from fastapi.testclient import TestClient

from verticals.nail.api.app import app


@pytest.fixture
def client():
    return TestClient(app)


class TestGetVerticals:
    def test_returns_200(self, client):
        resp = client.get("/api/verticals")
        assert resp.status_code == 200

    def test_body_has_verticals_key(self, client):
        resp = client.get("/api/verticals")
        data = resp.json()
        assert "verticals" in data

    def test_verticals_is_list(self, client):
        resp = client.get("/api/verticals")
        data = resp.json()
        assert isinstance(data["verticals"], list)

    def test_contains_nail(self, client):
        resp = client.get("/api/verticals")
        data = resp.json()
        verticals = data["verticals"]
        assert any(v["vertical"] == "nail" for v in verticals)

    def test_nail_has_required_fields(self, client):
        resp = client.get("/api/verticals")
        data = resp.json()
        nail = next((v for v in data["verticals"] if v["vertical"] == "nail"), None)
        assert nail is not None
        assert nail["vertical"] == "nail"
        assert nail["display_name"] == "美甲"
        assert nail["enabled"] is True
        assert "content_platforms" in nail
        assert "content_types" in nail
        assert "supported_reference_sources" in nail
        assert "default_page_count" in nail
        assert "workflow_id" in nail
        assert "case_enabled" in nail
        assert "reference_image_enabled" in nail

    def test_nail_content_platforms_includes_xhs(self, client):
        resp = client.get("/api/verticals")
        data = resp.json()
        nail = next((v for v in data["verticals"] if v["vertical"] == "nail"), None)
        assert "xhs" in nail["content_platforms"]

    def test_nail_content_types_includes_image_text_note(self, client):
        resp = client.get("/api/verticals")
        data = resp.json()
        nail = next((v for v in data["verticals"] if v["vertical"] == "nail"), None)
        assert "image_text_note" in nail["content_types"]

    def test_nail_supported_reference_sources(self, client):
        resp = client.get("/api/verticals")
        data = resp.json()
        nail = next((v for v in data["verticals"] if v["vertical"] == "nail"), None)
        assert nail["supported_reference_sources"] == ["none", "local_path", "case_id"]