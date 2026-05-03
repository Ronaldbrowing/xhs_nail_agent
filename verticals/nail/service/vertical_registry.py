"""
Vertical Registry — manages available verticals and their configurations.

Currently placed under verticals/nail/ as a temporary location.
Platform-level registry should migrate to src/service/vertical_registry.py
in a future milestone, with nail as a vertical adapter.
"""
from typing import Dict, List, Optional


class VerticalDefinition:
    """Schema for a vertical's configuration."""

    def __init__(
        self,
        vertical: str,
        display_name: str,
        enabled: bool = True,
        content_platforms: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        supported_reference_sources: Optional[List[str]] = None,
        default_page_count: int = 6,
        workflow_id: Optional[str] = None,
        case_enabled: bool = False,
        reference_image_enabled: bool = False,
    ):
        self.vertical = vertical
        self.display_name = display_name
        self.enabled = enabled
        self.content_platforms = content_platforms or []
        self.content_types = content_types or []
        self.supported_reference_sources = supported_reference_sources or []
        self.default_page_count = default_page_count
        self.workflow_id = workflow_id
        self.case_enabled = case_enabled
        self.reference_image_enabled = reference_image_enabled

    def to_dict(self) -> Dict:
        return {
            "vertical": self.vertical,
            "display_name": self.display_name,
            "enabled": self.enabled,
            "content_platforms": self.content_platforms,
            "content_types": self.content_types,
            "supported_reference_sources": self.supported_reference_sources,
            "default_page_count": self.default_page_count,
            "workflow_id": self.workflow_id,
            "case_enabled": self.case_enabled,
            "reference_image_enabled": self.reference_image_enabled,
        }


class VerticalRegistry:
    """
    Singleton registry of available verticals.

    Currently implemented as a simple in-memory store.
    MVP v1.0 only registers the 'nail' vertical.
    """

    _instance: Optional["VerticalRegistry"] = None

    def __init__(self):
        self._verticals: Dict[str, VerticalDefinition] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register the default nail vertical."""
        self.register(
            VerticalDefinition(
                vertical="nail",
                display_name="美甲",
                enabled=True,
                content_platforms=["xhs"],
                content_types=["image_text_note"],
                supported_reference_sources=["none", "local_path", "case_id"],
                default_page_count=6,
                workflow_id="nail_note_workflow_v1",
                case_enabled=True,
                reference_image_enabled=True,
            )
        )

    @classmethod
    def get_instance(cls) -> "VerticalRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, definition: VerticalDefinition) -> None:
        self._verticals[definition.vertical] = definition

    def get_vertical(self, vertical: str) -> Optional[VerticalDefinition]:
        return self._verticals.get(vertical)

    def list_verticals(self) -> List[VerticalDefinition]:
        return list(self._verticals.values())

    def is_valid_vertical(self, vertical: str) -> bool:
        """Check if a vertical is registered and enabled."""
        v = self._verticals.get(vertical)
        return v is not None and v.enabled