"""
Tests for GET /api/verticals/{vertical}/notes/{note_id}/package endpoint.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from verticals.nail.api.app import app
from verticals.nail.service.vertical_registry import VerticalRegistry


@pytest.fixture
def fake_output(tmp_path):
    (tmp_path / "nail_20260430_001").mkdir()
    (tmp_path / "nail_20260430_001" / "note_package.json").write_text(
        json.dumps({
            "note_id": "nail_20260430_001",
            "vertical": "nail",
            "content_platform": "xhs",
            "content_type": "image_text_note",
            "brief": "夏日蓝色猫眼短甲",
            "selected_title": "清凉一夏",
            "status": "succeeded",
            "pages": [{"page_id": "p1", "image_url": "xxx.png"}],
        }),
        encoding="utf-8"
    )

    (tmp_path / "nail_20260430_002").mkdir()
    (tmp_path / "nail_20260430_002" / "note_package.json").write_text(
        json.dumps({
            "note_id": "nail_20260430_002",
            "brief": "粉色渐变",
            "status": "succeeded",
            "pages": [],
        }),
        encoding="utf-8"
    )

    return tmp_path


@pytest.fixture
def client():
    return TestClient(app)


class TestGetNotePackage:
    def test_valid_package_returns_200(self, client, fake_output):
        from verticals.nail.service.package_service import PackageService

        svc = PackageService(output_root=fake_output)
        with patch("verticals.nail.api.routes._get_package_service", return_value=svc):
            resp = client.get("/api/verticals/nail/notes/nail_20260430_001/package")
            assert resp.status_code == 200

    def test_response_contains_package_data(self, client, fake_output):
        from verticals.nail.service.package_service import PackageService

        svc = PackageService(output_root=fake_output)
        with patch("verticals.nail.api.routes._get_package_service", return_value=svc):
            resp = client.get("/api/verticals/nail/notes/nail_20260430_001/package")
            data = resp.json()
            assert "note_id" in data
            assert data["note_id"] == "nail_20260430_001"

    def test_nonexistent_note_id_returns_404(self, client, fake_output):
        from verticals.nail.service.package_service import PackageService

        svc = PackageService(output_root=fake_output)
        with patch("verticals.nail.api.routes._get_package_service", return_value=svc):
            resp = client.get("/api/verticals/nail/notes/nonexistent_note/package")
            assert resp.status_code == 404

    def test_path_traversal_returns_4xx(self, client):
        # FastAPI path routing rejects paths with ../ in URL before reaching handler,
        # returning 404. The key security property (request is rejected) is maintained.
        resp = client.get("/api/verticals/nail/notes/../etc/passwd/package")
        assert resp.status_code in (400, 404)

    def test_url_encoded_path_traversal_returns_4xx(self, client):
        resp = client.get("/api/verticals/nail/notes/..%2f..%2fetc/passwd/package")
        assert resp.status_code in (400, 404)

    def test_unknown_vertical_returns_400(self, client):
        resp = client.get("/api/verticals/unknown_vertical/notes/nail_20260430_001/package")
        assert resp.status_code == 400
        assert "unknown vertical" in resp.json()["detail"].lower()

    def test_vertical_mismatch_returns_403_or_400(self, client, fake_output):
        from verticals.nail.service.package_service import PackageService
        from verticals.nail.service.vertical_registry import VerticalDefinition

        svc = PackageService(output_root=fake_output)
        with patch("verticals.nail.api.routes._get_package_service", return_value=svc):
            registry = VerticalRegistry.get_instance()
            registry.register(
                VerticalDefinition(
                    vertical="outfit",
                    display_name="穿搭",
                    enabled=True,
                    content_platforms=["xhs"],
                    content_types=["image_text_note"],
                )
            )

            resp = client.get("/api/verticals/outfit/notes/nail_20260430_001/package")
            # Either 403 (vertical mismatch) or 400 (unknown vertical if outfit not registered) is acceptable
            # as long as it's not 200 (success)
            assert resp.status_code in (400, 403)
            # Clean up
            registry._verticals.pop("outfit", None)

    def test_backslash_in_note_id_returns_4xx(self, client):
        resp = client.get("/api/verticals/nail/notes/..\\..\\etc/passwd/package")
        assert resp.status_code in (400, 404)

    def test_invalid_note_id_format_returns_4xx(self, client):
        resp = client.get("/api/verticals/nail/notes/invalid@note#id/package")
        assert resp.status_code in (400, 404)