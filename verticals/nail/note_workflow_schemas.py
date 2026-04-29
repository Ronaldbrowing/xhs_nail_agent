"""
NailNoteWorkflow schemas - Pydantic models for nail note workflow.
All new models use Pydantic BaseModel, compatible with v1 and v2.
"""
from enum import Enum
from typing import List, Optional, Any, Dict, Union
from dataclasses import dataclass, field

try:
    from pydantic import BaseModel, ConfigDict, Field
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseModel
    PYDANTIC_V2 = False


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class NoteGoal(str, Enum):
    """小红书笔记目标类型"""
    seed = "seed"           # 种草
    tutorial = "tutorial"   # 教程
    comparison = "comparison"  # 对比
    warning = "warning"     # 警示
    collection = "collection"  # 收藏
    conversion = "conversion"  # 转化


class PageRole(str, Enum):
    """笔记页面角色类型"""
    cover = "cover"                      # 封面主视觉
    detail_closeup = "detail_closeup"    # 细节特写
    skin_tone_fit = "skin_tone_fit"      # 肤色适配
    style_breakdown = "style_breakdown" # 款式拆解
    scene_mood = "scene_mood"            # 场景氛围
    avoid_mistakes = "avoid_mistakes"    # 避雷提示
    save_summary = "save_summary"        # 收藏总结
    materials = "materials"              # 素材工具
    step_by_step = "step_by_step"       # 步骤教程
    comparison_grid = "comparison_grid"  # 对比网格
    collection_grid = "collection_grid"  # 收藏网格


# ---------------------------------------------------------------------------
# VisualDNA
# ---------------------------------------------------------------------------

class VisualDNA(BaseModel):
    """视觉DNA - 确保多页生成时视觉一致性"""
    model_config = ConfigDict(extra='allow') if PYDANTIC_V2 else {}

    skin_tone: Optional[str] = None       # 肤色：黄皮/白皮/黑皮
    hand_model: Optional[str] = None      # 手型描述
    nail_length: Optional[str] = None     # 甲长：短甲/中长甲/长甲
    nail_shape: Optional[str] = None      # 甲型：短方圆/杏仁/尖形/方圆形
    main_color: Optional[str] = None     # 主色调
    finish: Optional[str] = None          # 质感：猫眼/冰透/镜面/磨砂
    lighting: Optional[str] = None        # 光线：自然光/暖光/冷光
    background: Optional[str] = None      # 背景
    style: Optional[str] = None           # 整体风格
    negative: List[str] = Field(default_factory=list)  # 负面清单
    source_reference: Optional[str] = None  # 参考图来源


# ---------------------------------------------------------------------------
# NotePageSpec
# ---------------------------------------------------------------------------

class NotePageSpec(BaseModel):
    """单页规格"""
    model_config = ConfigDict(extra='allow') if PYDANTIC_V2 else {}

    page_no: int
    role: PageRole
    goal: str                          # 该页的传播任务

    visual_brief: str                  # 视觉简报 - 该页要展示什么
    text_overlay: Optional[str] = None # 图片上的文字
    caption: Optional[str] = None     # 该页配文

    prompt: Optional[str] = None        # 图片生成Prompt
    negative_prompt: Optional[str] = None

    image_path: Optional[str] = None   # 生成后的图片路径（相对路径）
    image_url: Optional[str] = None
    used_reference: bool = False       # 是否使用了参考图

    status: str = "planned"           # planned/prompt_ready/generated/failed
    score: Optional[float] = None
    issues: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# NailNotePackage
# ---------------------------------------------------------------------------

class NailNotePackage(BaseModel):
    """完整的小红书美甲图文笔记发布包"""
    model_config = ConfigDict(extra='allow') if PYDANTIC_V2 else {}

    note_id: str
    brief: str
    style_id: Optional[str] = None
    note_goal: NoteGoal = NoteGoal.seed
    note_template: Optional[str] = None

    visual_dna: VisualDNA
    pages: List[NotePageSpec] = Field(default_factory=list)

    title_candidates: List[str] = Field(default_factory=list)
    selected_title: Optional[str] = None
    body: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    comment_hooks: List[str] = Field(default_factory=list)

    # 输出路径（相对路径）
    output_dir: Optional[str] = None
    package_path: Optional[str] = None
    archive_path: Optional[str] = None

    success: bool = False
    partial_failure: bool = False
    diagnostics: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# NailNoteUserInput - 扩展用户输入
# ---------------------------------------------------------------------------

class NailNoteUserInput:
    """
    扩展用户输入，兼容原有 UserInput 字段。
    这是一个 dataclass 而非 Pydantic model，用于接收用户参数。
    """
    def __init__(
        self,
        brief: str,
        style_id: Optional[str] = None,
        skin_tone: Optional[str] = None,
        nail_length: Optional[str] = None,
        nail_shape: Optional[str] = None,
        note_goal: str = "seed",
        note_template: Optional[str] = None,
        page_count: int = 6,
        allow_text_on_image: bool = False,
        reference_image_path: Optional[str] = None,
        case_id: Optional[str] = None,
        generate_images: bool = True,
        generate_copy: bool = True,
        generate_tags: bool = True,
        quality: str = "final",
        aspect: str = "3:4",
        direction: str = "balanced",
        # 兼容原有字段
        color_preferences: Optional[List[str]] = None,
        avoid_elements: Optional[List[str]] = None,
        audience: Optional[str] = None,
        season: Optional[str] = None,
        **kwargs
    ):
        self.brief = brief
        self.style_id = style_id
        self.skin_tone = skin_tone
        self.nail_length = nail_length
        self.nail_shape = nail_shape
        self.note_goal = note_goal
        self.note_template = note_template
        self.page_count = page_count
        self.allow_text_on_image = allow_text_on_image
        self.reference_image_path = reference_image_path
        self.case_id = case_id
        self.generate_images = generate_images
        self.generate_copy = generate_copy
        self.generate_tags = generate_tags
        self.quality = quality
        self.aspect = aspect
        self.direction = direction
        self.color_preferences = color_preferences or []
        self.avoid_elements = avoid_elements or []
        self.audience = audience
        self.season = season
        self._extra = kwargs

    def to_dict(self) -> dict:
        """转为字典"""
        result = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def model_to_dict(model) -> dict:
    """Pydantic model 转 dict，兼容 v1 和 v2"""
    if PYDANTIC_V2 and hasattr(model, 'model_dump'):
        return model.model_dump()
    elif hasattr(model, 'dict'):
        return model.dict()
    return vars(model)


def model_to_json(model) -> str:
    """Pydantic model 转 JSON 字符串，兼容 v1 和 v2"""
    if PYDANTIC_V2 and hasattr(model, 'model_dump_json'):
        return model.model_dump_json()
    return json.dumps(model_to_dict(model), ensure_ascii=False)


import json
