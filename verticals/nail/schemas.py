from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

# Re-export NailNoteWorkflow types for convenient importing from verticals.nail.schemas
from .note_workflow_schemas import (
    NailNoteUserInput,
    NailNotePackage,
    NoteGoal,
    PageRole,
    VisualDNA,
    NotePageSpec,
)

@dataclass
class UserInput:
    brief: str
    style_id: Optional[str] = None
    audience: Optional[str] = None
    season: Optional[str] = None
    skin_tone: Optional[str] = None
    nail_length: Optional[str] = None
    nail_shape: Optional[str] = None
    color_preferences: List[str] = field(default_factory=list)
    avoid_elements: List[str] = field(default_factory=list)
    reference_image_path: Optional[str] = None
    reference_usage: Optional[str] = None
    reference_must_keep: List[str] = field(default_factory=list)
    reference_can_change: List[str] = field(default_factory=list)
    allow_text_on_image: bool = False
    need_preview: bool = True
    note_goal: Optional[str] = None
    scene_hint: Optional[str] = None

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
