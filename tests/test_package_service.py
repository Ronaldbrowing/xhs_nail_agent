"""
Tests for PackageService.
"""
import json
import pytest
from pathlib import Path

from verticals.nail.service.package_service import PackageService


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

    (tmp_path / "nail_20260430_003_broken").mkdir()
    (tmp_path / "nail_20260430_003_broken" / "note_package.json").write_text(
        "{ broken", encoding="utf-8"
    )

    return tmp_path


class TestPackageServiceFind:
    def test_loads_valid_package(self, fake_output):
        svc = PackageService(output_root=fake_output)
        pkg = svc.load_package("nail", "nail_20260430_001")
        assert pkg["note_id"] == "nail_20260430_001"
        assert pkg["vertical"] == "nail"

    def test_missing_note_id_raises_file_not_found(self, fake_output):
        svc = PackageService(output_root=fake_output)
        with pytest.raises(FileNotFoundError):
            svc.load_package("nail", "nonexistent_note_id")

    def test_invalid_note_id_raises_value(self, fake_output):
        svc = PackageService(output_root=fake_output)
        with pytest.raises(ValueError):
            svc.load_package("nail", "../etc/passwd")

    def test_path_traversal_raises_value(self, fake_output):
        svc = PackageService(output_root=fake_output)
        with pytest.raises(ValueError):
            svc.load_package("nail", "..%2f..%2fetc%2fpasswd")

    def test_corrupted_json_raises_value(self, fake_output):
        svc = PackageService(output_root=fake_output)
        with pytest.raises(ValueError) as exc:
            svc.load_package("nail", "nail_20260430_003_broken")
        assert "corrupted" in str(exc.value).lower()

    def test_vertical_mismatch_raises_permission(self, fake_output):
        svc = PackageService(output_root=fake_output)
        with pytest.raises(PermissionError) as exc:
            svc.load_package("outfit", "nail_20260430_001")
        assert "mismatch" in str(exc.value).lower()

    def test_missing_fields_get_inferred(self, fake_output):
        svc = PackageService(output_root=fake_output)
        pkg = svc.load_package("nail", "nail_20260430_002")
        assert pkg["content_platform"] == "xhs"
        assert pkg["content_type"] == "image_text_note"
        assert pkg["_field_sources"]["content_platform"] == "inferred"
        assert pkg["_field_sources"]["content_type"] == "inferred"

    def test_explicit_fields_marked_explicit(self, fake_output):
        svc = PackageService(output_root=fake_output)
        pkg = svc.load_package("nail", "nail_20260430_001")
        assert pkg["_field_sources"]["vertical"] == "explicit"
        assert pkg["_field_sources"]["content_platform"] == "explicit"
        assert pkg["_field_sources"]["content_type"] == "explicit"

    def test_inferred_vertical_when_package_missing(self, fake_output):
        svc = PackageService(output_root=fake_output)
        pkg = svc.load_package("nail", "nail_20260430_002")
        assert pkg["_field_sources"]["vertical"] == "inferred"
        assert pkg["vertical"] == "nail"

    def test_vertical_inference_requires_prefix_match(self, fake_output, tmp_path):
        (tmp_path / "outfit_20260430_999").mkdir()
        (tmp_path / "outfit_20260430_999" / "note_package.json").write_text(
            json.dumps({"note_id": "outfit_20260430_999", "pages": []}),
            encoding="utf-8"
        )
        svc = PackageService(output_root=tmp_path)
        pkg = svc.load_package("outfit", "outfit_20260430_999")
        assert pkg["_field_sources"]["vertical"] == "inferred"
        assert pkg["vertical"] == "outfit"

    def test_backslash_in_note_id_rejected(self, fake_output):
        svc = PackageService(output_root=fake_output)
        with pytest.raises(ValueError):
            svc.load_package("nail", "nail_20260430_001\\etc")

    def test_note_id_with_special_chars_rejected(self, fake_output):
        svc = PackageService(output_root=fake_output)
        with pytest.raises(ValueError):
            svc.load_package("nail", "nail_20260430_001;ls")

    def test_find_package_returns_field_sources(self, fake_output):
        svc = PackageService(output_root=fake_output)
        data, field_sources = svc.find_package("nail", "nail_20260430_001")
        assert isinstance(field_sources, dict)
        assert "vertical" in field_sources
        assert "content_platform" in field_sources
        assert "content_type" in field_sources