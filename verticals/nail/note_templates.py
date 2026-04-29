"""
笔记模板 - 根据 note_goal + style_id 返回页面角色列表
"""
from dataclasses import dataclass
from typing import List, Tuple
from .note_workflow_schemas import PageRole


# ---------------------------------------------------------------------------
# 页面角色模板定义
# ---------------------------------------------------------------------------

@dataclass
class PageRoleSpec:
    """单页模板规格"""
    page_id: str
    role: PageRole
    goal: str                          # 该页的传播任务描述
    visual_guidance: str               # 视觉指导
    copy_guidance: str                # 文案指导


# ---------------------------------------------------------------------------
# Seed 种草模板（默认6页）
# ---------------------------------------------------------------------------

SEED_TEMPLATES: List[PageRoleSpec] = [
    PageRoleSpec(
        page_id="cover",
        role=PageRole.cover,
        goal="抓点击 - 第一时间吸引用户眼球，激发点击欲望",
        visual_guidance="主视觉大图，展示最终效果全貌，简洁背景突出指甲",
        copy_guidance="标题党风格，引发好奇"
    ),
    PageRoleSpec(
        page_id="detail_closeup",
        role=PageRole.detail_closeup,
        goal="展示猫眼光泽和甲面质感",
        visual_guidance="近距离特写，展示猫眼磁粉的玻璃感光泽",
        copy_guidance="细节描述，引发对质感的向往"
    ),
    PageRoleSpec(
        page_id="skin_tone_fit",
        role=PageRole.skin_tone_fit,
        goal="解决黄皮显白顾虑",
        visual_guidance="黄皮手部试色对比，展示显白效果",
        copy_guidance="痛点切入，说明黄皮显白原理"
    ),
    PageRoleSpec(
        page_id="style_breakdown",
        role=PageRole.style_breakdown,
        goal="提供颜色、甲型、质感等复刻信息",
        visual_guidance="分解展示：颜色/甲型/质感/搭配",
        copy_guidance="给美甲师的复刻关键词"
    ),
    PageRoleSpec(
        page_id="scene_mood",
        role=PageRole.scene_mood,
        goal="增加夏日生活方式代入",
        visual_guidance="生活场景图，海边/咖啡厅/约会等",
        copy_guidance="场景种草，增加代入感"
    ),
    PageRoleSpec(
        page_id="save_summary",
        role=PageRole.save_summary,
        goal="促收藏，给美甲师看的总结",
        visual_guidance="总结卡片，关键词提炼",
        copy_guidance="收藏引导，互动钩子"
    ),
]


# ---------------------------------------------------------------------------
# Tutorial 教程模板
# ---------------------------------------------------------------------------

TUTORIAL_TEMPLATES: List[PageRoleSpec] = [
    PageRoleSpec(
        page_id="cover",
        role=PageRole.cover,
        goal="吸引教程目标用户",
        visual_guidance="成品图 + 教程标签",
        copy_guidance="教程标题"
    ),
    PageRoleSpec(
        page_id="step_by_step",
        role=PageRole.step_by_step,
        goal="分步骤展示制作过程",
        visual_guidance="步骤分解图",
        copy_guidance="每步说明"
    ),
    PageRoleSpec(
        page_id="materials",
        role=PageRole.materials,
        goal="展示所需材料和工具",
        visual_guidance="材料清单图",
        copy_guidance="材料说明"
    ),
    PageRoleSpec(
        page_id="detail_closeup",
        role=PageRole.detail_closeup,
        goal="关键步骤特写",
        visual_guidance="难点细节特写",
        copy_guidance="技巧说明"
    ),
    PageRoleSpec(
        page_id="scene_mood",
        role=PageRole.scene_mood,
        goal="成品场景展示",
        visual_guidance="成品生活场景图",
        copy_guidance="成品描述"
    ),
    PageRoleSpec(
        page_id="save_summary",
        role=PageRole.save_summary,
        goal="收藏引导 + 常见问题",
        visual_guidance="总结 + 常见问题卡片",
        copy_guidance="收藏引导"
    ),
]


# ---------------------------------------------------------------------------
# 其他模板（简化）
# ---------------------------------------------------------------------------

COMPARISON_TEMPLATES: List[PageRoleSpec] = [
    PageRoleSpec(page_id="cover", role=PageRole.cover, goal="对比主题封面",
                 visual_guidance="对比主题封面图", copy_guidance="对比标题"),
    PageRoleSpec(page_id="comparison_grid", role=PageRole.comparison_grid,
                 goal="多款对比", visual_guidance="对比网格图", copy_guidance="对比说明"),
    PageRoleSpec(page_id="detail_closeup", role=PageRole.detail_closeup,
                 goal="各自细节", visual_guidance="细节图", copy_guidance="细节描述"),
    PageRoleSpec(page_id="scene_mood", role=PageRole.scene_mood,
                 goal="各自适合场景", visual_guidance="场景图", copy_guidance="场景说明"),
    PageRoleSpec(page_id="save_summary", role=PageRole.save_summary,
                 goal="总结推荐", visual_guidance="总结卡片", copy_guidance="推荐引导"),
    PageRoleSpec(page_id="avoid_mistakes", role=PageRole.avoid_mistakes,
                 goal="避雷提示", visual_guidance="避雷图", copy_guidance="避雷说明"),
]

WARNING_TEMPLATES: List[PageRoleSpec] = [
    PageRoleSpec(page_id="cover", role=PageRole.cover, goal="警示主题封面",
                 visual_guidance="警示封面", copy_guidance="警示标题"),
    PageRoleSpec(page_id="avoid_mistakes", role=PageRole.avoid_mistakes,
                 goal="雷区展示", visual_guidance="雷区图", copy_guidance="雷区说明"),
    PageRoleSpec(page_id="style_breakdown", role=PageRole.style_breakdown,
                 goal="正确做法", visual_guidance="正确做法图", copy_guidance="正确说明"),
    PageRoleSpec(page_id="detail_closeup", role=PageRole.detail_closeup,
                 goal="关键细节", visual_guidance="细节图", copy_guidance="细节"),
    PageRoleSpec(page_id="save_summary", role=PageRole.save_summary,
                 goal="正确总结", visual_guidance="总结", copy_guidance="总结引导"),
    PageRoleSpec(page_id="scene_mood", role=PageRole.scene_mood,
                 goal="正向场景", visual_guidance="正向场景", copy_guidance="正向说明"),
]

COLLECTION_TEMPLATES: List[PageRoleSpec] = [
    PageRoleSpec(page_id="cover", role=PageRole.cover, goal="收藏主题封面",
                 visual_guidance="收藏封面", copy_guidance="收藏标题"),
    PageRoleSpec(page_id="collection_grid", role=PageRole.collection_grid,
                 goal="合集展示", visual_guidance="合集网格", copy_guidance="合集说明"),
    PageRoleSpec(page_id="detail_closeup", role=PageRole.detail_closeup,
                 goal="单品特写1", visual_guidance="单品图", copy_guidance="单品描述"),
    PageRoleSpec(page_id="detail_closeup", role=PageRole.detail_closeup,
                 goal="单品特写2", visual_guidance="单品图", copy_guidance="单品描述"),
    PageRoleSpec(page_id="scene_mood", role=PageRole.scene_mood,
                 goal="场景搭配", visual_guidance="场景图", copy_guidance="场景说明"),
    PageRoleSpec(page_id="save_summary", role=PageRole.save_summary,
                 goal="收藏引导", visual_guidance="总结", copy_guidance="收藏引导"),
]

CONVERSION_TEMPLATES: List[PageRoleSpec] = [
    PageRoleSpec(page_id="cover", role=PageRole.cover, goal="转化封面",
                 visual_guidance="产品图", copy_guidance="转化标题"),
    PageRoleSpec(page_id="style_breakdown", role=PageRole.style_breakdown,
                 goal="卖点拆解", visual_guidance="卖点图", copy_guidance="卖点"),
    PageRoleSpec(page_id="skin_tone_fit", role=PageRole.skin_tone_fit,
                 goal="适合人群", visual_guidance="人群图", copy_guidance="人群说明"),
    PageRoleSpec(page_id="detail_closeup", role=PageRole.detail_closeup,
                 goal="细节质感", visual_guidance="细节图", copy_guidance="细节"),
    PageRoleSpec(page_id="scene_mood", role=PageRole.scene_mood,
                 goal="使用场景", visual_guidance="场景图", copy_guidance="场景"),
    PageRoleSpec(page_id="save_summary", role=PageRole.save_summary,
                 goal="行动引导", visual_guidance="行动卡片", copy_guidance="行动引导"),
]


# ---------------------------------------------------------------------------
# 模板映射
# ---------------------------------------------------------------------------

_TEMPLATES = {
    "seed": SEED_TEMPLATES,
    "tutorial": TUTORIAL_TEMPLATES,
    "comparison": COMPARISON_TEMPLATES,
    "warning": WARNING_TEMPLATES,
    "collection": COLLECTION_TEMPLATES,
    "conversion": CONVERSION_TEMPLATES,
}


def get_note_template(note_goal: str, page_count: int = 6) -> List[PageRoleSpec]:
    """
    根据 note_goal 返回页面角色模板列表。
    
    Args:
        note_goal: 笔记目标类型 (seed/tutorial/comparison/warning/collection/conversion)
        page_count: 期望页数（暂未实现按页数截取，固定返回模板定义的数量）
    
    Returns:
        PageRoleSpec 列表
    """
    note_goal = note_goal or "seed"
    templates = _TEMPLATES.get(note_goal, SEED_TEMPLATES)
    
    # 如果 page_count > 默认数量，可以加入 avoid_mistakes
    if page_count > len(templates):
        # 加入避雷页
        extra = PageRoleSpec(
            page_id="avoid_mistakes",
            role=PageRole.avoid_mistakes,
            goal="避雷提示",
            visual_guidance="避雷图",
            copy_guidance="避雷说明"
        )
        templates = templates + [extra]
    
    return templates[:page_count]


def get_page_role_goals(note_goal: str, page_count: int = 6) -> List[Tuple[PageRole, str]]:
    """
    返回 (PageRole, goal_str) 元组列表。
    用于 note_planner 生成页面规划。
    """
    specs = get_note_template(note_goal, page_count)
    return [(spec.role, spec.goal) for spec in specs]
