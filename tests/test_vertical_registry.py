"""
Tests for VerticalRegistry.
"""
import pytest
from verticals.nail.service.vertical_registry import VerticalRegistry, VerticalDefinition


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset the singleton before each test."""
    VerticalRegistry._instance = None
    yield
    VerticalRegistry._instance = None


class TestVerticalRegistry:
    def test_get_instance_returns_singleton(self):
        r1 = VerticalRegistry.get_instance()
        r2 = VerticalRegistry.get_instance()
        assert r1 is r2

    def test_list_verticals_returns_nail(self):
        registry = VerticalRegistry.get_instance()
        verticals = registry.list_verticals()
        assert len(verticals) >= 1
        assert any(v.vertical == "nail" for v in verticals)

    def test_get_vertical_nail_exists(self):
        registry = VerticalRegistry.get_instance()
        nail = registry.get_vertical("nail")
        assert nail is not None
        assert nail.vertical == "nail"
        assert nail.display_name == "美甲"

    def test_get_vertical_unknown_returns_none(self):
        registry = VerticalRegistry.get_instance()
        unknown = registry.get_vertical("unknown_vertical")
        assert unknown is None

    def test_is_valid_vertical_nail_true(self):
        registry = VerticalRegistry.get_instance()
        assert registry.is_valid_vertical("nail") is True

    def test_is_valid_vertical_unknown_false(self):
        registry = VerticalRegistry.get_instance()
        assert registry.is_valid_vertical("unknown_vertical") is False

    def test_nail_vertical_definition_fields(self):
        registry = VerticalRegistry.get_instance()
        nail = registry.get_vertical("nail")
        assert nail.content_platforms == ["xhs"]
        assert nail.content_types == ["image_text_note"]
        assert nail.supported_reference_sources == ["none", "local_path", "case_id"]
        assert nail.default_page_count == 6
        assert nail.workflow_id == "nail_note_workflow_v1"
        assert nail.case_enabled is True
        assert nail.reference_image_enabled is True

    def test_register_new_vertical(self):
        registry = VerticalRegistry.get_instance()
        new_def = VerticalDefinition(
            vertical="outfit",
            display_name="穿搭",
            enabled=True,
            content_platforms=["xhs"],
            content_types=["image_text_note"],
        )
        registry.register(new_def)
        assert registry.is_valid_vertical("outfit") is True
        assert registry.get_vertical("outfit").display_name == "穿搭"

    def test_to_dict_includes_all_fields(self):
        registry = VerticalRegistry.get_instance()
        nail = registry.get_vertical("nail")
        d = nail.to_dict()
        assert d["vertical"] == "nail"
        assert d["display_name"] == "美甲"
        assert d["enabled"] is True
        assert d["content_platforms"] == ["xhs"]
        assert d["content_types"] == ["image_text_note"]
        assert d["supported_reference_sources"] == ["none", "local_path", "case_id"]
        assert d["default_page_count"] == 6
        assert d["workflow_id"] == "nail_note_workflow_v1"
        assert d["case_enabled"] is True
        assert d["reference_image_enabled"] is True