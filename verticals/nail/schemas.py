from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .note_workflow_schemas import (
    NailNotePackage,
    NailNoteUserInput,
    NoteGoal,
    NotePageSpec,
    PageRole,
    VisualDNA,
)


class UserInput(NailNoteUserInput):
    """
    Backward-compatible user input surface.

    Historically callers imported UserInput from verticals.nail.schemas.
    Keep that import working while exposing the newer NailNoteWorkflow fields.
    """

    def __init__(
        self,
        brief: str,
        style_id: Optional[str] = None,
        audience: Optional[str] = None,
        season: Optional[str] = None,
        skin_tone: Optional[str] = None,
        nail_length: Optional[str] = None,
        nail_shape: Optional[str] = None,
        color_preferences: Optional[List[str]] = None,
        avoid_elements: Optional[List[str]] = None,
        reference_image_path: Optional[str] = None,
        reference_usage: Optional[str] = None,
        reference_must_keep: Optional[List[str]] = None,
        reference_can_change: Optional[List[str]] = None,
        allow_text_on_image: bool = False,
        need_preview: bool = True,
        note_goal: str = "seed",
        scene_hint: Optional[str] = None,
        note_template: Optional[str] = None,
        page_count: int = 6,
        case_id: Optional[str] = None,
        generate_images: bool = True,
        generate_copy: bool = True,
        generate_tags: bool = True,
        quality: str = "final",
        aspect: str = "3:4",
        direction: str = "balanced",
        **kwargs,
    ):
        super().__init__(
            brief=brief,
            style_id=style_id,
            skin_tone=skin_tone,
            nail_length=nail_length,
            nail_shape=nail_shape,
            note_goal=note_goal,
            note_template=note_template,
            page_count=page_count,
            allow_text_on_image=allow_text_on_image,
            reference_image_path=reference_image_path,
            case_id=case_id,
            generate_images=generate_images,
            generate_copy=generate_copy,
            generate_tags=generate_tags,
            quality=quality,
            aspect=aspect,
            direction=direction,
            color_preferences=color_preferences,
            avoid_elements=avoid_elements,
            audience=audience,
            season=season,
            **kwargs,
        )
        self.reference_usage = reference_usage
        self.reference_must_keep = reference_must_keep or []
        self.reference_can_change = reference_can_change or []
        self.need_preview = need_preview
        self.scene_hint = scene_hint


@dataclass
class ReferenceDNA:
    subject: str = ""
    hand_model: str = ""
    nail_shape: str = ""
    nail_length: str = ""
    dominant_colors: List[str] = field(default_factory=list)
    finish_types: List[str] = field(default_factory=list)
    decorations: List[str] = field(default_factory=list)
    composition: str = ""
    background: str = ""
    lighting: str = ""
    mood: str = ""
    title_area_hint: str = ""
    main_visual_identity: List[str] = field(default_factory=list)


@dataclass
class NailStyle:
    style_id: str
    style_name: str
    scene_type: str
    task: str
    direction: str
    aspect: str
    target_audience: str
    visual: Dict[str, Any]
    copywriting: Dict[str, Any]
    tags: Dict[str, Any]
    image_prompt: Dict[str, Any]
    reference_policy: Dict[str, Any]


@dataclass
class PromptBundle:
    final_brief: str
    image_prompt: str
    copy_prompt: str
    title_candidates: List[str]
    body_candidates: List[str]
    tag_candidates: List[List[str]]
    debug_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PreviewPayload:
    cover_prompt: str
    titles: List[str]
    bodies: List[str]
    tags: List[List[str]]
    selected_style: str
    dna_summary: Optional[Dict[str, Any]] = None
