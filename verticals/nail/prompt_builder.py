from typing import Optional
from .schemas import UserInput, NailStyle, ReferenceDNA

def join_list(items):
    return "、".join([str(x) for x in items if x])

def build_image_prompt(user_input: UserInput, style: NailStyle, dna: Optional[ReferenceDNA] = None) -> str:
    visual = style.visual
    prompt_cfg = style.image_prompt
    ref_policy = style.reference_policy

    parts = [
        "你正在为小红书美甲图文笔记生成封面图。",
        "核心要求：指甲清晰、手部自然、构图可点击、适合收藏、适合小红书封面。",
        f"任务场景：{style.scene_type}",
        f"任务类型：{style.task}",
        f"风格强度：{style.direction}",
        f"画面比例：{style.aspect}",
        f"目标用户：{style.target_audience}",
        f"用户需求：{user_input.brief}",
        "",
        "【Style 视觉要求】",
        f"构图：{visual.get('composition', '')}",
        f"手部：{visual.get('hand_model', '')}",
        f"甲型：{visual.get('nail_shape', '')}",
        f"甲长：{visual.get('nail_length', '')}",
        f"推荐色系：{join_list(visual.get('color_palette', []))}",
        f"质感效果：{join_list(visual.get('finish', []))}",
        f"装饰元素：{join_list(visual.get('decorations', []))}",
        f"背景：{visual.get('background', '')}",
        f"光线：{visual.get('lighting', '')}",
        f"文字策略：{visual.get('text_policy', '')}",
        f"标题区域：{visual.get('title_area', '')}"
    ]

    if user_input.skin_tone:
        parts.append(f"用户额外肤色要求：{user_input.skin_tone}")
    if user_input.nail_length:
        parts.append(f"用户额外甲长要求：{user_input.nail_length}")
    if user_input.nail_shape:
        parts.append(f"用户额外甲型要求：{user_input.nail_shape}")
    if user_input.color_preferences:
        parts.append(f"用户偏好颜色：{join_list(user_input.color_preferences)}")
    if user_input.avoid_elements:
        parts.append(f"用户明确避开：{join_list(user_input.avoid_elements)}")

    if dna:
        fields = ref_policy.get("dna_fields_to_use", [])
        parts.extend(["", "【参考图 DNA】"])
        parts.append(f"参考图用途：{user_input.reference_usage or '默认作为款式和构图参考'}")
        if "subject" in fields:
            parts.append(f"主体结构参考：{dna.subject}")
        if "hand_model" in fields:
            parts.append(f"手部参考：{dna.hand_model}")
        if "nail_shape" in fields:
            parts.append(f"参考甲型：{dna.nail_shape}")
        if "nail_length" in fields:
            parts.append(f"参考甲长：{dna.nail_length}")
        if "dominant_colors" in fields:
            parts.append(f"参考主色：{join_list(dna.dominant_colors)}")
        if "finish_types" in fields:
            parts.append(f"参考质感：{join_list(dna.finish_types)}")
        if "decorations" in fields:
            parts.append(f"参考装饰：{join_list(dna.decorations)}")
        if "composition" in fields:
            parts.append(f"参考构图：{dna.composition}")
        if "background" in fields:
            parts.append(f"参考背景：{dna.background}")
        if "lighting" in fields:
            parts.append(f"参考光线：{dna.lighting}")
        parts.append(f"参考图核心身份：{join_list(dna.main_visual_identity)}")
        parts.append(f"模板要求必须保留：{join_list(ref_policy.get('must_preserve', []))}")
        parts.append(f"模板允许变化：{join_list(ref_policy.get('allow_variation', []))}")
        parts.append(f"参考继承强度：{ref_policy.get('inherit_strength', 0.7)}")

    parts.extend(["", "【必须满足】"])
    for item in prompt_cfg.get("positive_constraints", []):
        parts.append(f"- {item}")
    for item in prompt_cfg.get("must_show", []):
        parts.append(f"- must show: {item}")

    parts.extend(["", "【必须避免】"])
    for item in prompt_cfg.get("negative_constraints", []):
        parts.append(f"- {item}")
    for item in prompt_cfg.get("avoid", []):
        parts.append(f"- avoid: {item}")

    if not user_input.allow_text_on_image:
        parts.append("- 不要直接生成中文标题、文字、乱码、水印；只保留干净标题留白，文字由后期添加。")

    return "\n".join(parts)
