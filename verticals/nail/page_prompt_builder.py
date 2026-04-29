"""
页面 Prompt 编译器 - 将 NotePageSpec + VisualDNA + UserInput 编译成每页完整 Prompt
"""
from typing import Optional
from .note_workflow_schemas import NotePageSpec, VisualDNA, PageRole


# ---------------------------------------------------------------------------
# 角色特定的 Prompt 前缀
# ---------------------------------------------------------------------------

_ROLE_PROMPTS = {
    PageRole.cover: (
        "小红书美甲封面图，精致主视觉。"
        "画面主体是自然亚洲女性手部，展示最终美甲效果。"
    ),
    PageRole.detail_closeup: (
        "小红书美甲细节特写图，高清近距离拍摄。"
        "重点展示猫眼光泽感和甲面质感。"
    ),
    PageRole.skin_tone_fit: (
        "美甲肤色对比图，"
        "黄皮手部试色对比效果。"
    ),
    PageRole.style_breakdown: (
        "美甲款式拆解图，"
        "清晰展示颜色、甲型、质感三要素。"
    ),
    PageRole.scene_mood: (
        "小红书美甲生活场景图，"
        "夏日氛围感，高颜值场景。"
    ),
    PageRole.avoid_mistakes: (
        "美甲避雷对比图，"
        "错误示范与正确做法对比。"
    ),
    PageRole.save_summary: (
        "美甲笔记总结图，"
        "关键信息卡片风格。"
    ),
    PageRole.materials: (
        "美甲材料和工具展示图，"
        "产品清单风格。"
    ),
    PageRole.step_by_step: (
        "美甲教程步骤图，"
        "分步骤展示制作过程。"
    ),
    PageRole.comparison_grid: (
        "多款美甲对比网格图，"
        "同一风格不同款式对比。"
    ),
    PageRole.collection_grid: (
        "美甲合集网格图，"
        "同色系或同风格款式汇总。"
    ),
}


# ---------------------------------------------------------------------------
# 核心编译函数
# ---------------------------------------------------------------------------

def _build_negative_prompt(visual_dna: VisualDNA, role: PageRole) -> str:
    """构建负面提示词"""
    negatives = list(visual_dna.negative) if visual_dna.negative else []
    negatives.extend([
        "水印", "文字", "多余手指", "畸形手部",
        "指甲过长", "甲面不平", "气泡杂质",
        "背景杂乱", "过度磨皮", "美颜过度",
    ])
    return ", ".join(negatives)


def _compose_prompt_parts(
    role: PageRole,
    visual_dna: VisualDNA,
    brief: str = "",
    page_goal: str = "",
    visual_brief: str = "",
    text_overlay: Optional[str] = None,
    allow_text: bool = False,
) -> dict:
    """
    组合 Prompt 各部分。
    返回 {'prompt': str, 'negative_prompt': str}
    """
    role_prefix = _ROLE_PROMPTS.get(role, "小红书美甲图片。")

    shared_visual = ["【共享视觉DNA】"]
    if brief:
        shared_visual.append("用户需求：{brief}".format(brief=brief))
    if visual_dna.hand_model:
        shared_visual.append("手型：{value}".format(value=visual_dna.hand_model))
    if visual_dna.skin_tone:
        shared_visual.append("肤色：{value}".format(value=visual_dna.skin_tone))
    if visual_dna.nail_shape:
        shared_visual.append("甲型：{value}".format(value=visual_dna.nail_shape))
    if visual_dna.nail_length:
        shared_visual.append("甲长：{value}".format(value=visual_dna.nail_length))
    if visual_dna.main_color:
        shared_visual.append("主色：{value}".format(value=visual_dna.main_color))
    if visual_dna.finish:
        shared_visual.append("质感：{value}".format(value=visual_dna.finish))
    if visual_dna.lighting:
        shared_visual.append("光线：{value}".format(value=visual_dna.lighting))
    if visual_dna.background:
        shared_visual.append("背景：{value}".format(value=visual_dna.background))
    if visual_dna.style:
        shared_visual.append("风格：{value}".format(value=visual_dna.style))
    shared_visual.append("参考图继承要求：如存在参考图，继承配色逻辑、材质质感与构图氛围，但不要机械复制。")

    page_goal_lines = [
        "【当前页面目标】",
        "page role: {role}".format(role=role.value if hasattr(role, "value") else role),
        "角色描述：{prefix}".format(prefix=role_prefix),
    ]
    if page_goal:
        page_goal_lines.append("page goal: {goal}".format(goal=page_goal))
    if visual_brief:
        page_goal_lines.append("visual brief: {brief}".format(brief=visual_brief))

    output_requirements = [
        "【输出要求】",
        "小红书图文风格",
        "高质感",
        "无水印",
        "不要错误文字",
    ]
    if allow_text and text_overlay:
        output_requirements.append("如需排版，可预留清晰文字区域，建议文案：{text}".format(text=text_overlay))

    prompt = "\n".join(shared_visual + [""] + page_goal_lines + [""] + output_requirements)
    negative = _build_negative_prompt(visual_dna, role)

    return {"prompt": prompt, "negative_prompt": negative}


def build_page_prompt(
    page: NotePageSpec,
    visual_dna: VisualDNA,
    user_input,
) -> NotePageSpec:
    """
    为 NotePageSpec 编译 prompt 和 negative_prompt。

    Args:
        page: NotePageSpec（会被原地修改）
        visual_dna: VisualDNA
        user_input: NailNoteUserInput

    Returns:
        修改后的 NotePageSpec
    """
    brief = getattr(user_input, 'brief', '') or ''
    allow_text = getattr(user_input, 'allow_text_on_image', False)
    text_overlay = page.text_overlay
    page_goal = page.goal or ''
    visual_brief = page.visual_brief or ''

    result = _compose_prompt_parts(
        role=page.role,
        visual_dna=visual_dna,
        brief=brief,
        page_goal=page_goal,
        visual_brief=visual_brief,
        text_overlay=text_overlay,
        allow_text=allow_text,
    )

    page.prompt = result["prompt"]
    page.negative_prompt = result["negative_prompt"]
    page.status = "prompt_ready"

    return page
