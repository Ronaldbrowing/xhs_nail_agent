from typing import Any, Dict, List, Optional

try:
    from pydantic import BaseModel, ConfigDict, Field
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseModel, Field
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
    quality: str = "draft"
    aspect: str = "3:4"
    direction: str = "balanced"
    reference_image_path: Optional[str] = None
    case_id: Optional[str] = None
    max_workers: int = 1

    def to_user_input(self) -> NailNoteUserInput:
        if PYDANTIC_V2:
            data = self.model_dump()
        else:
            data = self.dict()
        return NailNoteUserInput(**data)


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
