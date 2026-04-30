"""
Tests for GET /api/verticals/{vertical}/notes endpoint.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from verticals.nail.api.app import app


@pytest.fixture
def client():
    return TestClient(app)


class TestListNotes:
    def test_nail_returns_200(self, client):
        mock_svc = MagicMock()
        mock_svc.list_notes.return_value = [
            {
                "note_id": "nail_20260430_001",
                "vertical": "nail",
                "content_platform": "xhs",
                "content_type": "image_text_note",
                "scenario": None,
                "brief": "夏日蓝色猫眼短甲",
                "selected_title": "清凉一夏",
                "status": "succeeded",
                "created_at": "2026-04-30T10:00:00Z",
                "has_package": True,
                "field_sources": {
                    "vertical": "explicit",
                    "content_platform": "explicit",
                    "content_type": "explicit",
                },
            }
        ]

        with patch("verticals.nail.api.routes._get_history_service", return_value=mock_svc):
            resp = client.get("/api/verticals/nail/notes")
            assert resp.status_code == 200

    def test_response_has_items_key(self, client):
        mock_svc = MagicMock()
        mock_svc.list_notes.return_value = []

        with patch("verticals.nail.api.routes._get_history_service", return_value=mock_svc):
            resp = client.get("/api/verticals/nail/notes")
            data = resp.json()
            assert "items" in data

    def test_response_has_total_key(self, client):
        mock_svc = MagicMock()
        mock_svc.list_notes.return_value = []

        with patch("verticals.nail.api.routes._get_history_service", return_value=mock_svc):
            resp = client.get("/api/verticals/nail/notes")
            data = resp.json()
            assert "total" in data

    def test_response_has_vertical_key(self, client):
        mock_svc = MagicMock()
        mock_svc.list_notes.return_value = []

        with patch("verticals.nail.api.routes._get_history_service", return_value=mock_svc):
            resp = client.get("/api/verticals/nail/notes")
            data = resp.json()
            assert "vertical" in data
            assert data["vertical"] == "nail"

    def test_items_contain_note_fields(self, client):
        mock_svc = MagicMock()
        mock_svc.list_notes.return_value = [
            {
                "note_id": "n1",
                "vertical": "nail",
                "content_platform": "xhs",
                "content_type": "image_text_note",
                "scenario": None,
                "brief": None,
                "selected_title": None,
                "status": "succeeded",
                "created_at": "2026-04-30T10:00:00Z",
                "has_package": True,
                "field_sources": {
                    "vertical": "explicit",
                    "content_platform": "explicit",
                    "content_type": "explicit",
                },
            }
        ]

        with patch("verticals.nail.api.routes._get_history_service", return_value=mock_svc):
            resp = client.get("/api/verticals/nail/notes")
            data = resp.json()
            if data["items"]:
                item = data["items"][0]
                assert "note_id" in item
                assert "vertical" in item
                assert "content_platform" in item
                assert "content_type" in item
                assert "status" in item
                assert "created_at" in item
                assert "has_package" in item
                assert "field_sources" in item

    def test_unknown_vertical_returns_400(self, client):
        resp = client.get("/api/verticals/unknown_vertical/notes")
        assert resp.status_code == 400
        assert "unknown vertical" in resp.json()["detail"].lower()

    def test_empty_history_returns_items_empty(self, client):
        mock_svc = MagicMock()
        mock_svc.list_notes.return_value = []

        with patch("verticals.nail.api.routes._get_history_service", return_value=mock_svc):
            resp = client.get("/api/verticals/nail/notes")
            assert resp.status_code == 200
            data = resp.json()
            assert data["items"] == []
            assert data["total"] == 0