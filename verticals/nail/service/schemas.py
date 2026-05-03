import re
from typing import Any, Dict, List, Optional, Literal

try:
    from pydantic import BaseModel, ConfigDict, Field, root_validator, validator
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseModel, Field, root_validator, validator
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
    reference_source: Optional[Literal["none", "local_path", "case_id"]] = None
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

    @validator("reference_image_path", "case_id", "reference_source", pre=True)
    def normalize_optional_strings(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
        return value

    @root_validator(skip_on_failure=True)
    def validate_reference_source(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        source = values.get("reference_source")
        reference_image_path = values.get("reference_image_path")
        case_id = values.get("case_id")

        if source is None:
            if reference_image_path and case_id:
                raise ValueError("reference_image_path and case_id cannot both be set")
            if reference_image_path:
                source = "local_path"
            elif case_id:
                source = "case_id"
            else:
                source = "none"

        if source == "none":
            if reference_image_path or case_id:
                raise ValueError("reference_source=none does not allow reference_image_path or case_id")
        elif source == "local_path":
            if not reference_image_path:
                raise ValueError("reference_source=local_path requires reference_image_path")
            if case_id:
                raise ValueError("reference_source=local_path does not allow case_id")
        elif source == "case_id":
            if not case_id:
                raise ValueError("reference_source=case_id requires case_id")
            if reference_image_path:
                raise ValueError("reference_source=case_id does not allow reference_image_path")

        values["reference_source"] = source
        values["reference_image_path"] = reference_image_path
        values["case_id"] = case_id
        return values


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
