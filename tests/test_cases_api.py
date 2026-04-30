"""
Tests for case library APIs.
"""
import json

import pytest
from fastapi.testclient import TestClient

from verticals.nail.api.app import app
from verticals.nail.service.case_service import CaseService
from verticals.nail.service.vertical_registry import VerticalDefinition, VerticalRegistry


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def fake_case_root(tmp_path):
    case_root = tmp_path / "case_library"
    poster_dir = case_root / "poster"
    product_dir = case_root / "product"
    poster_dir.mkdir(parents=True)
    product_dir.mkdir(parents=True)

    poster_case = poster_dir / "case_038_summer_blue"
    poster_case.mkdir()
    (poster_case / "metadata.json").write_text(
        json.dumps(
            {
                "case_id": "case_038",
                "brief": "夏日蓝色猫眼",
                "created_at": "2026-04-30T12:00:00Z",
                "tags": ["夏日"],
            }
        ),
        encoding="utf-8",
    )
    (poster_case / "image.png").write_bytes(b"png")

    product_case = product_dir / "case_038_product"
    product_case.mkdir()
    (product_case / "metadata.json").write_text(
        json.dumps(
            {
                "case_id": "case_038",
                "brief": "产品案例",
                "created_at": "2026-04-30T11:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (product_case / "image.png").write_bytes(b"png")

    return case_root


class TestCasesApi:
    def test_list_cases_returns_200_for_nail(self, client, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        from unittest.mock import patch

        with patch("verticals.nail.api.routes._get_case_service", return_value=svc):
            resp = client.get("/api/verticals/nail/cases")
            assert resp.status_code == 200
            data = resp.json()
            assert data["vertical"] == "nail"
            assert data["total"] == 1
            assert data["items"][0]["case_id"] == "case_038"

    def test_get_case_returns_detail(self, client, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        from unittest.mock import patch

        with patch("verticals.nail.api.routes._get_case_service", return_value=svc):
            resp = client.get("/api/verticals/nail/cases/case_038")
            assert resp.status_code == 200
            data = resp.json()
            assert data["case_id"] == "case_038"
            assert data["vertical"] == "nail"
            assert data["image_path"].startswith("case_library/poster/")

    def test_unknown_vertical_returns_400(self, client):
        resp = client.get("/api/verticals/unknown_vertical/cases")
        assert resp.status_code == 400
        assert "unknown vertical" in resp.json()["detail"].lower()

    def test_unknown_case_id_returns_404(self, client, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        from unittest.mock import patch

        with patch("verticals.nail.api.routes._get_case_service", return_value=svc):
            resp = client.get("/api/verticals/nail/cases/case_404")
            assert resp.status_code == 404

    def test_case_lookup_respects_vertical_scope(self, client, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        svc._VERTICAL_TASK_MAP["outfit"] = "product"
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
        from unittest.mock import patch

        try:
            with patch("verticals.nail.api.routes._get_case_service", return_value=svc):
                resp = client.get("/api/verticals/outfit/cases/case_038")
                assert resp.status_code == 200
                data = resp.json()
                assert data["vertical"] == "outfit"
                assert data["task"] == "product"
                assert data["brief"] == "产品案例"
        finally:
            registry._verticals.pop("outfit", None)
            svc._VERTICAL_TASK_MAP.pop("outfit", None)
