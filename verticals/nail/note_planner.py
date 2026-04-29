"""
笔记规划器 - 根据模板生成 NotePageSpec 列表
"""
from typing import List, Tuple, Optional
from .note_workflow_schemas import NotePageSpec, PageRole, VisualDNA
from src.llm_provider import get_text_client, get_text_model


def _generate_visual_brief_llm(role: PageRole, brief: str, visual_dna: VisualDNA) -> str:
    """用 LLM 生成该页的 visual_brief"""
    try:
        client = get_text_client()
        role_descriptions = {
            PageRole.cover: "封面主视觉 - 抓眼球，展示最终效果全貌",
            PageRole.detail_closeup: "细节特写 - 展示质感、光泽、工艺",
            PageRole.skin_tone_fit: "肤色适配 - 展示不同肤色的效果",
            PageRole.style_breakdown: "款式拆解 - 分解颜色、甲型、质感",
            PageRole.scene_mood: "场景氛围 - 生活方式代入",
            PageRole.avoid_mistakes: "避雷提示 - 常见错误和注意事项",
            PageRole.save_summary: "收藏总结 - 关键信息提炼",
            PageRole.materials: "素材工具 - 所需材料和工具",
            PageRole.step_by_step: "步骤教程 - 制作过程分解",
            PageRole.comparison_grid: "对比网格 - 多款对比",
            PageRole.collection_grid: "收藏网格 - 合集展示",
        }
        role_desc = role_descriptions.get(role, str(role.value))
        
        prompt = f"""根据以下美甲需求，为「第{role_desc}」这一页生成视觉简报（visual_brief）。

用户需求：{brief}
指甲长度：{visual_dna.nail_length or '未指定'}
指甲形状：{visual_dna.nail_shape or '未指定'}
主色调：{visual_dna.main_color or '未指定'}
质感：{visual_dna.finish or '未指定'}
肤色：{visual_dna.skin_tone or '未指定'}
风格：{visual_dna.style or '未指定'}

请生成一句简洁的视觉描述，说明这一页应该展示什么具体内容。不超过50字。

只返回描述，不要其他文字。"""

        response = client.chat.completions.create(
            model=get_text_model("planner_small"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=100,
        )
        text = response.choices[0].message.content.strip()
        if text:
            return text
    except Exception:
        pass
    
    # Fallback: 规则生成
    return _generate_visual_brief_rules(role, brief, visual_dna)


def _generate_visual_brief_rules(role: PageRole, brief: str, visual_dna: VisualDNA) -> str:
    """用规则生成 visual_brief"""
    briefs = {
        PageRole.cover: f"展示{visual_dna.nail_length or '短甲'}{visual_dna.nail_shape or '方圆'}的最终效果全貌，{visual_dna.main_color or '清透色'}{visual_dna.finish or '质感'}，{visual_dna.style or '清透显白'}风格",
        PageRole.detail_closeup: f"近距离特写{visual_dna.main_color or '清透'}猫眼光泽，展示甲面{visual_dna.finish or '质感'}和细腻度",
        PageRole.skin_tone_fit: f"黄皮/白皮手部试色对比，展示{visual_dna.main_color or '该颜色'}在{visual_dna.skin_tone or '黄皮'}上的显白效果",
        PageRole.style_breakdown: f"分解展示：{visual_dna.main_color or '颜色'}/{visual_dna.nail_shape or '甲型'}/{visual_dna.finish or '质感'}三要素，给美甲师参考",
        PageRole.scene_mood: f"夏日生活场景图，{visual_dna.main_color or '清透蓝'}搭配{visual_dna.style or '夏日'}氛围，可海边可约会",
        PageRole.avoid_mistakes: f"展示常见雷区：过长甲型/暗沉颜色/廉价闪粉，对比正确做法",
        PageRole.save_summary: f"总结卡片：{visual_dna.main_color or '清透蓝猫眼'}/{visual_dna.nail_shape or '短方圆'}/{visual_dna.skin_tone or '黄皮显白'}关键词提炼",
        PageRole.materials: f"展示所需材料：{visual_dna.main_color or '清透蓝'}甲油胶/猫眼磁粉/加固胶等",
        PageRole.step_by_step: f"分步骤展示：前置处理→底胶→{visual_dna.main_color or '颜色'}甲油→猫眼磁粉→封层",
        PageRole.comparison_grid: f"多款{visual_dna.main_color or '清透'}美甲对比网格，展示不同风格",
        PageRole.collection_grid: f"{visual_dna.style or '夏日'}风格美甲合集网格，{visual_dna.main_color or '清透色'}系汇总",
    }
    return briefs.get(role, f"展示{role.value}页面，{brief}")


def plan_note_pages(
    user_input,
    visual_dna: VisualDNA,
    role_goal_pairs: List[Tuple[PageRole, str]]
) -> List[NotePageSpec]:
    """
    根据角色-目标对列表，生成 NotePageSpec 列表。

    Args:
        user_input: NailNoteUserInput
        visual_dna: VisualDNA
        role_goal_pairs: [(PageRole, goal_str), ...]

    Returns:
        NotePageSpec 列表
    """
    brief = getattr(user_input, 'brief', '') or ''
    pages = []

    for i, (role, goal) in enumerate(role_goal_pairs):
        page_no = i + 1

        # 生成 visual_brief
        visual_brief = _generate_visual_brief_llm(role, brief, visual_dna)

        # 生成 text_overlay 和 caption
        text_overlay, caption = _generate_text_overlay_and_caption_llm(role, brief, visual_dna)

        page = NotePageSpec(
            page_no=page_no,
            role=role,
            goal=goal,
            visual_brief=visual_brief,
            text_overlay=text_overlay,
            caption=caption,
            status="planned",
        )
        pages.append(page)

    return pages


def _generate_text_overlay_and_caption_llm(role: PageRole, brief: str, visual_dna: VisualDNA) -> Tuple[Optional[str], Optional[str]]:
    """用 LLM 为该页生成 text_overlay（图片文字）和 caption（配文）"""
    text_overlay = None
    caption = None

    try:
        client = get_text_client()
        role_text_overlay_descriptions = {
            PageRole.cover: "封面大标题，如「夏日显白猫眼✨」",
            PageRole.detail_closeup: "细节标签，如「猫眼光泽绝了」",
            PageRole.skin_tone_fit: "对比说明，如「黄皮显白攻略」",
            PageRole.style_breakdown: "要素标签，如「颜色·甲型·质感」",
            PageRole.scene_mood: "氛围文案，如「海边约会必备」",
            PageRole.avoid_mistakes: "避雷提示，如「做错毁所有」",
            PageRole.save_summary: "总结金句，如「收藏！超全美甲攻略」",
            PageRole.materials: "材料清单标题，如「需要的材料都在这」",
            PageRole.step_by_step: "步骤引导，如「跟我做！超简单」",
            PageRole.comparison_grid: "对比说明，如「哪款最适合你」",
            PageRole.collection_grid: "合集标题，如「私藏6款绝美猫眼」",
        }
        role_caption_descriptions = {
            PageRole.cover: "吸引点击的开头，如「姐妹们！这也太好看了吧」",
            PageRole.detail_closeup: "强调质感的描述，如「阳光下绝美光泽」",
            PageRole.skin_tone_fit: "肤色适配说明，如「黄皮亲测显白」",
            PageRole.style_breakdown: "款式拆解说明，如「三个要点教你选对款式」",
            PageRole.scene_mood: "场景氛围描述，如「约会/通勤/度假都能hold住」",
            PageRole.avoid_mistakes: "避雷提醒，如「这几个坑千万别踩」",
            PageRole.save_summary: "收藏引导，如「建议收藏！超全美甲指南」",
            PageRole.materials: "材料介绍，如「新手友好！需要的都在这」",
            PageRole.step_by_step: "教程引导，如「跟着做不出错」",
            PageRole.comparison_grid: "对比总结，如「测评结果出炉」",
            PageRole.collection_grid: "合集推荐，如「私藏宝藏款式」",
        }

        overlay_hint = role_text_overlay_descriptions.get(role, "简短有力的文字")
        caption_hint = role_caption_descriptions.get(role, "配合图片的简短文案")

        prompt = f"""根据以下美甲页面信息，生成该页的：
1. text_overlay：图片上叠加的文字（简短有力，10字以内，适合小红书风格）
2. caption：图片配文（配合图片的说明文字，20-50字）

页面角色：{role.value}
用户需求：{brief}
甲长：{visual_dna.nail_length or '未指定'}
甲型：{visual_dna.nail_shape or '未指定'}
主色调：{visual_dna.main_color or '未指定'}
质感：{visual_dna.finish or '未指定'}
风格：{visual_dna.style or '未指定'}

text_overlay 示例：{overlay_hint}
caption 示例：{caption_hint}

请直接返回，格式如下（两行）：
text_overlay: <文字>
caption: <配文>

只返回这两行，不要其他文字。"""

        response = client.chat.completions.create(
            model=get_text_model("planner_small"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150,
        )
        text = response.choices[0].message.content.strip()
        lines = text.split('\n')
        for line in lines:
            if line.startswith('text_overlay:'):
                text_overlay = line.split(':', 1)[1].strip()
            elif line.startswith('caption:'):
                caption = line.split(':', 1)[1].strip()
    except Exception:
        pass

    # Fallback
    if text_overlay is None:
        text_overlay = _text_overlay_fallback(role, brief, visual_dna)
    if caption is None:
        caption = _caption_fallback(role, brief, visual_dna)

    return text_overlay, caption


def _text_overlay_fallback(role: PageRole, brief: str, visual_dna: VisualDNA) -> str:
    """规则生成 text_overlay fallback"""
    overlays = {
        PageRole.cover: f"{visual_dna.main_color or '美甲'}{visual_dna.finish or '款'}✨",
        PageRole.detail_closeup: "绝美国货✨",
        PageRole.skin_tone_fit: f"{visual_dna.skin_tone or '黄皮'}显白攻略",
        PageRole.style_breakdown: "三要素拆解",
        PageRole.scene_mood: f"{visual_dna.style or '夏日'}必备",
        PageRole.avoid_mistakes: "避雷必看⚠️",
        PageRole.save_summary: "建议收藏✅",
        PageRole.materials: "材料清单📦",
        PageRole.step_by_step: "跟我做👆",
        PageRole.comparison_grid: "测评对比",
        PageRole.collection_grid: "私藏合集",
    }
    return overlays.get(role, "美甲✨")


def _caption_fallback(role: PageRole, brief: str, visual_dna: VisualDNA) -> str:
    """规则生成 caption fallback"""
    captions = {
        PageRole.cover: f"姐妹们！{visual_dna.main_color or '这款'}{visual_dna.nail_shape or '美甲'}{visual_dna.finish or ''}也太好看了吧✨",
        PageRole.detail_closeup: f"阳光下{visual_dna.main_color or '这颜色'}的猫眼光泽绝了",
        PageRole.skin_tone_fit: f"{visual_dna.skin_tone or '黄皮'}亲测{visual_dna.main_color or '这个颜色'}超级显白",
        PageRole.style_breakdown: f"颜色·甲型·质感三要素教你选对款式",
        PageRole.scene_mood: f"{visual_dna.style or '夏日'}氛围感满满，约会通勤都适合",
        PageRole.avoid_mistakes: f"这几个坑美甲师不会告诉你的",
        PageRole.save_summary: f"建议收藏！超全{visual_dna.main_color or '美甲'}攻略",
        PageRole.materials: f"新手友好！做{visual_dna.main_color or '这款'}需要这些材料",
        PageRole.step_by_step: f"跟我做！简单几步搞定{visual_dna.main_color or '这款'}",
        PageRole.comparison_grid: f"多款{visual_dna.main_color or '美甲'}测评，哪款最适合你",
        PageRole.collection_grid: f"私藏{visual_dna.main_color or '美甲'}款式合集",
    }
    return captions.get(role, f"{visual_dna.main_color or '美甲'}{visual_dna.nail_shape or ''}{visual_dna.finish or ''}，超好看✨")
