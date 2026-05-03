"""
Vertical Registry — manages available verticals and their configurations.

Platform-level registry for multi-vertical support.
Each vertical is represented by a VerticalDefinition and optionally a VerticalAdapter.

VerticalAdapter Interface (for v2.0 multi-vertical):
-------------------------------------------------
A vertical adapter must provide:

    workflow: str
        - Identifier for the workflow orchestrator to use
        - e.g., "nail_note_workflow_v1", "poster_workflow_v1"

    case_dir: Path
        - Path to the vertical's case library directory
        - e.g., "case_library/nail"

    form_fields: List[FormFieldDef]
        - Schema for the vertical's request/creation form
        - Each field: {name, label, type, required, options, default}

    label_maps: Dict[str, Dict[str, str]]
        - Localized label translations for display
        - e.g., {"content_type": {"xhs": "小红书", "dy": "抖音"}, ...}

    # Methods the adapter must implement:

    def get_workflow(self) -> str:
        '''Return the workflow identifier for this vertical.'''

    def get_case_dir(self) -> Path:
        '''Return the case library directory for this vertical.'''

    def get_form_fields(self) -> List[FormFieldDef]:
        '''Return the form schema for note creation.'''

    def get_label_map(self, key: str) -> Dict[str, str]:
        '''Return the label translation map for a given key.'''

    def validate_request(self, request_data: Dict) -> ValidationResult:
        '''Validate a creation request against vertical-specific rules.'''

    def compile_prompt(self, request_data: Dict) -> CompiledPrompt:
        '''Compile the design prompt for image generation.'''

Implementation Note (v1.0):
    Currently only the 'nail' vertical exists. VerticalAdapter is documented
    but not yet implemented — awaiting a second vertical to extract common logic.
    The registry singleton is initialized with default verticals.
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
        platform_labels: Optional[Dict[str, str]] = None,
        content_type_labels: Optional[Dict[str, str]] = None,
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
        self.platform_labels = platform_labels or {}
        self.content_type_labels = content_type_labels or {}

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
            "platform_labels": self.platform_labels,
            "content_type_labels": self.content_type_labels,
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
                platform_labels={"xhs": "小红书"},
                content_type_labels={"image_text_note": "图文笔记"},
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
