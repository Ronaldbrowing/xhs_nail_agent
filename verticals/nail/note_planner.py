"""
笔记规划器 - 根据模板生成 NotePageSpec 列表
"""
from typing import List, Tuple
from .note_workflow_schemas import NotePageSpec, PageRole, VisualDNA


def _generate_visual_brief_llm(role: PageRole, brief: str, visual_dna: VisualDNA) -> str:
    """用 LLM 生成该页的 visual_brief"""
    try:
        import os
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key)
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
                model="gpt-4o-mini",
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
        
        page = NotePageSpec(
            page_no=page_no,
            role=role,
            goal=goal,
            visual_brief=visual_brief,
            status="planned",
        )
        pages.append(page)
    
    return pages
