import re
from typing import Any, Dict, List, Optional, Literal

try:
    from pydantic import BaseModel, ConfigDict, Field, validator
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseModel, Field, validator
    ConfigDict = dict
    PYDANTIC_V2 = False

from verticals.nail.note_workflow_schemas import NailNoteUserInput


class _Model(BaseModel):
    if PYDANTIC_V2:
        model_config = ConfigDict(extra="forbid")


class NailNoteCreateRequest(_Model):
    brief: str
    style_id: Optional[str] = None
    skin_tone: Optional[str] = None
    nail_length: Optional[str] = None
    nail_shape: Optional[str] = None
    note_goal: str = "seed"
    page_count: int = 6
    generate_images: bool = True
    generate_copy: bool = True
    generate_tags: bool = True
    quality: Literal["draft", "final", "premium"] = "draft"
    aspect: Literal["1:1", "3:4", "4:3", "16:9", "9:16"] = "3:4"
    direction: Literal["conservative", "balanced", "bold"] = "balanced"
    reference_image_path: Optional[str] = None
    case_id: Optional[str] = None
    max_workers: int = Field(default=1, ge=1, le=2)

    def as_dict(self) -> Dict[str, Any]:
        if PYDANTIC_V2:
            return self.model_dump()
        return self.dict()

    def to_user_input(self, request_id: Optional[str] = None) -> NailNoteUserInput:
        payload = self.as_dict()
        if request_id:
            payload["request_id"] = request_id
        return NailNoteUserInput(**payload)

    @validator("style_id")
    def validate_style_id(cls, value: Optional[str]) -> Optional[str]:
        if value in (None, ""):
            return value
        if not re.fullmatch(r"[A-Za-z0-9_/-]{1,64}", value):
            raise ValueError("style_id must match [A-Za-z0-9_/-]{1,64}")
        return value


class NailNotePageResponse(_Model):
    page_no: int
    role: str
    status: str
    image_path: Optional[str] = None
    used_reference: bool = False
    issues: List[str] = Field(default_factory=list)


class NailNoteCreateResponse(_Model):
    request_id: str
    note_id: Optional[str] = None
    status: str
    package_path: Optional[str] = None
    output_dir: Optional[str] = None
    success: bool = False
    partial_failure: bool = False
    qa_score: Optional[float] = None
    pages: List[NailNotePageResponse] = Field(default_factory=list)
    diagnostics: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
