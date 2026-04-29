from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from case_library import get_case_image_path, get_case_metadata
from case_reference_resolver import try_resolve_case_image_path
from project_paths import resolve_project_path, to_project_relative


@dataclass
class ReferenceContext:
    source_type: str
    reference_image_path: Optional[str] = None
    case_id: Optional[str] = None
    resolved_image_path: Optional[str] = None
    resolved_image_name: Optional[str] = None
    dna_summary: Optional[str] = None
    dna_source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    @property
    def has_reference(self) -> bool:
        return bool(self.resolved_image_path)


def build_case_dna_summary_from_metadata(case_meta: Optional[Dict[str, Any]]) -> Optional[str]:
    if not case_meta:
        return None

    brief = str(case_meta.get("brief") or "").strip()
    prompt = str(case_meta.get("prompt") or "").strip()
    params = case_meta.get("params") or {}
    tags = case_meta.get("tags") or []
    rating = case_meta.get("rating", 0)

    if "【参考图DNA摘要】" in prompt:
        prompt = prompt.split("【参考图DNA摘要】", 1)[0].strip()

    text_pool = "\n".join([brief, prompt, " ".join(str(tag) for tag in tags)])
    keyword_rules = [
        ("清透", "清透感"),
        ("透亮", "透亮质感"),
        ("玻璃", "玻璃感"),
        ("猫眼", "猫眼光泽"),
        ("珠光", "珠光反射"),
        ("渐变", "渐变过渡"),
        ("蓝", "蓝色系"),
        ("粉", "粉色系"),
        ("裸", "裸色系"),
        ("短甲", "短甲形态"),
        ("长甲", "长甲形态"),
        ("法式", "法式边缘设计"),
        ("夏日", "夏日清爽氛围"),
        ("小红书", "小红书封面风格"),
        ("封面", "封面式构图"),
        ("留白", "留白构图"),
        ("高级", "高级感"),
        ("极简", "极简风格"),
        ("甜美", "甜美风格"),
    ]

    style_hints = []
    for keyword, label in keyword_rules:
        if keyword in text_pool and label not in style_hints:
            style_hints.append(label)

    if not style_hints:
        style_hints.append("历史案例中的视觉风格、构图逻辑和质感表达")

    dna_parts = [
        "请参考历史案例的视觉 DNA，但不要机械复制原图。",
        "历史案例主题：{brief}".format(brief=brief[:160] if brief else "未记录"),
        "风格关键词：{keywords}".format(keywords="、".join(style_hints)),
        "任务类型参考：{task}".format(task=params.get("task", case_meta.get("task", "poster"))),
        "画面比例参考：{aspect}".format(aspect=params.get("aspect", "未记录")),
        "设计方向参考：{direction}".format(direction=params.get("direction", "未记录")),
        "历史评分参考：{rating}".format(rating=rating),
        "继承重点：配色逻辑、材质质感、画面氛围、主体呈现方式、构图留白。",
        "变化要求：根据当前新需求重新生成，不要一比一复刻历史案例。",
    ]

    if tags:
        dna_parts.insert(4, "案例标签：{tags}".format(tags="、".join(str(tag) for tag in tags[:8])))

    if prompt:
        dna_parts.append("历史 prompt 摘要：{prompt}".format(prompt=prompt[:300]))

    return "\n".join(dna_parts)


def _build_local_path_context(reference_image_path: str) -> ReferenceContext:
    resolved = resolve_project_path(reference_image_path)
    if not resolved.exists():
        raise FileNotFoundError("reference_image_path not found: {path}".format(path=reference_image_path))

    return ReferenceContext(
        source_type="local_path",
        reference_image_path=reference_image_path,
        resolved_image_path=str(resolved),
        resolved_image_name=resolved.name,
        dna_source="local_path",
    )


def _resolve_case_image(case_id: str, task: str) -> Optional[str]:
    image_path = get_case_image_path(case_id, task)
    if image_path:
        return image_path
    return try_resolve_case_image_path(case_id, task)


def _build_case_id_context(case_id: str, task: str) -> ReferenceContext:
    image_path = _resolve_case_image(case_id, task)
    if not image_path:
        raise FileNotFoundError("case_id not found or has no image: {case_id}".format(case_id=case_id))

    resolved = resolve_project_path(image_path)
    if not resolved.exists():
        raise FileNotFoundError("case image not found: {path}".format(path=image_path))

    metadata = get_case_metadata(case_id, task)
    dna_summary = build_case_dna_summary_from_metadata(metadata)

    return ReferenceContext(
        source_type="case_id",
        reference_image_path=None,
        case_id=case_id,
        resolved_image_path=str(resolved),
        resolved_image_name=resolved.name,
        dna_summary=dna_summary,
        dna_source="case_metadata" if dna_summary else None,
        metadata=metadata,
    )


def build_reference_context(
    user_input,
    task: str = "poster",
    allow_reference_override: bool = False,
) -> ReferenceContext:
    reference_image_path = getattr(user_input, "reference_image_path", None)
    case_id = getattr(user_input, "case_id", None)

    if reference_image_path and case_id and not allow_reference_override:
        raise ValueError("reference_image_path and case_id cannot both be set")

    if reference_image_path:
        return _build_local_path_context(reference_image_path)

    if case_id:
        return _build_case_id_context(case_id, task)

    return ReferenceContext(source_type="none")


def reference_context_to_diagnostics(context: ReferenceContext) -> Dict[str, Any]:
    return {
        "source_type": context.source_type,
        "case_id": context.case_id,
        "reference_image_path": context.reference_image_path,
        "resolved_image_path": to_project_relative(context.resolved_image_path) if context.resolved_image_path else None,
        "resolved_image_name": context.resolved_image_name,
        "dna_summary_included": bool(context.dna_summary),
        "dna_source": context.dna_source,
        "error": context.error,
    }
