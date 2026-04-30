"""
Tests for HistoryService.
"""
import json
import pytest
from pathlib import Path

from verticals.nail.service.history_service import HistoryService


@pytest.fixture
def fake_output(tmp_path):
    """Create a fake output directory with note packages."""
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
            "created_at": "2026-04-30T10:00:00Z",
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
            "created_at": "2026-04-30T11:00:00Z",
            "pages": [],
        }),
        encoding="utf-8"
    )

    (tmp_path / "nail_20260430_003_broken").mkdir()
    (tmp_path / "nail_20260430_003_broken" / "note_package.json").write_text(
        "{ broken json", encoding="utf-8"
    )

    (tmp_path / "other_20260430_004").mkdir()
    (tmp_path / "other_20260430_004" / "note_package.json").write_text(
        json.dumps({
            "note_id": "other_20260430_004",
            "vertical": "other",
            "created_at": "2026-04-30T12:00:00Z",
            "pages": [{"page_id": "p1", "image_url": "xxx.png"}],
        }),
        encoding="utf-8"
    )

    return tmp_path


class TestHistoryServiceListNotes:
    def test_scans_output_returns_nail_notes(self, fake_output):
        svc = HistoryService(output_root=fake_output)
        items = svc.list_notes("nail")
        note_ids = [item["note_id"] for item in items]
        assert "nail_20260430_001" in note_ids
        assert "nail_20260430_002" in note_ids

    def test_filters_by_vertical(self, fake_output):
        svc = HistoryService(output_root=fake_output)
        items = svc.list_notes("nail")
        for item in items:
            assert item["vertical"] == "nail"

    def test_missing_fields_get_inferred(self, fake_output):
        svc = HistoryService(output_root=fake_output)
        items = svc.list_notes("nail")
        item002 = next(i for i in items if i["note_id"] == "nail_20260430_002")
        assert item002["content_platform"] == "xhs"
        assert item002["content_type"] == "image_text_note"
        assert item002["field_sources"]["content_platform"] == "inferred"
        assert item002["field_sources"]["content_type"] == "inferred"

    def test_explicit_fields_marked_explicit(self, fake_output):
        svc = HistoryService(output_root=fake_output)
        items = svc.list_notes("nail")
        item001 = next(i for i in items if i["note_id"] == "nail_20260430_001")
        assert item001["field_sources"]["vertical"] == "explicit"
        assert item001["field_sources"]["content_platform"] == "explicit"
        assert item001["field_sources"]["content_type"] == "explicit"

    def test_broken_package_skipped(self, fake_output):
        svc = HistoryService(output_root=fake_output)
        items = svc.list_notes("nail")
        note_ids = [item["note_id"] for item in items]
        assert "nail_20260430_003_broken" not in note_ids

    def test_empty_output_returns_empty_list(self, tmp_path):
        svc = HistoryService(output_root=tmp_path)
        items = svc.list_notes("nail")
        assert items == []

    def test_has_package_true_when_pages_exist(self, fake_output):
        svc = HistoryService(output_root=fake_output)
        items = svc.list_notes("nail")
        item001 = next(i for i in items if i["note_id"] == "nail_20260430_001")
        assert item001["has_package"] is True

    def test_has_package_false_when_no_pages(self, fake_output):
        svc = HistoryService(output_root=fake_output)
        items = svc.list_notes("nail")
        item002 = next(i for i in items if i["note_id"] == "nail_20260430_002")
        assert item002["has_package"] is False

    def test_get_total_returns_count(self, fake_output):
        svc = HistoryService(output_root=fake_output)
        assert svc.get_total("nail") == 2

    def test_field_sources_present(self, fake_output):
        svc = HistoryService(output_root=fake_output)
        items = svc.list_notes("nail")
        for item in items:
            assert "field_sources" in item
            assert "vertical" in item["field_sources"]
            assert "content_platform" in item["field_sources"]
            assert "content_type" in item["field_sources"]