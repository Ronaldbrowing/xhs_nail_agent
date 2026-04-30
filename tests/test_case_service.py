"""
Tests for CaseService.
"""
import json
from pathlib import Path

import pytest

from verticals.nail.service.case_service import CaseService


@pytest.fixture
def fake_case_root(tmp_path: Path) -> Path:
    case_root = tmp_path / "case_library"
    poster_dir = case_root / "poster"
    product_dir = case_root / "product"
    poster_dir.mkdir(parents=True)
    product_dir.mkdir(parents=True)

    case038 = poster_dir / "case_038_summer_blue"
    case038.mkdir()
    (case038 / "metadata.json").write_text(
        json.dumps(
            {
                "case_id": "case_038",
                "brief": "夏日蓝色猫眼",
                "tags": ["夏日", "猫眼"],
                "rating": 5,
                "created_at": "2026-04-30T12:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (case038 / "image.png").write_bytes(b"png")

    broken = poster_dir / "case_999_broken"
    broken.mkdir()
    (broken / "metadata.json").write_text("{ broken", encoding="utf-8")

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


class TestCaseService:
    def test_list_cases_for_nail_returns_poster_cases(self, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        items = svc.list_cases("nail")
        assert len(items) == 1
        assert items[0]["case_id"] == "case_038"
        assert items[0]["vertical"] == "nail"
        assert items[0]["task"] == "poster"
        assert items[0]["has_image"] is True

    def test_get_case_returns_detail(self, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        item = svc.get_case("nail", "case_038")
        assert item["case_id"] == "case_038"
        assert item["brief"] == "夏日蓝色猫眼"
        assert item["image_path"].startswith("case_library/poster/case_038_summer_blue/")

    def test_unknown_case_id_raises_file_not_found(self, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        with pytest.raises(FileNotFoundError):
            svc.get_case("nail", "case_404")

    def test_invalid_case_id_raises_value(self, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        with pytest.raises(ValueError):
            svc.get_case("nail", "../etc/passwd")

    def test_unknown_vertical_raises_value(self, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        with pytest.raises(ValueError):
            svc.list_cases("unknown_vertical")

    def test_vertical_mapping_prevents_fallback_to_other_task(self, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        svc._VERTICAL_TASK_MAP["outfit"] = "product"
        try:
            item = svc.get_case("outfit", "case_038")
            assert item["task"] == "product"
            assert item["brief"] == "产品案例"
        finally:
            svc._VERTICAL_TASK_MAP.pop("outfit", None)

    def test_broken_case_metadata_is_skipped_from_list(self, fake_case_root):
        svc = CaseService(case_root=fake_case_root)
        items = svc.list_cases("nail")
        case_ids = [item["case_id"] for item in items]
        assert "case_999" not in case_ids
