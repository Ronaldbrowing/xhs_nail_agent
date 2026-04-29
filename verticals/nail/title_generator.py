"""
标题生成器 - 生成10+个标题候选
"""
from typing import List
from .note_workflow_schemas import VisualDNA
from src.llm_provider import get_text_client, get_text_model


def _get_llm_client():
    try:
        return get_text_client()
    except Exception:
        pass
    return None


def generate_title_candidates(user_input, visual_dna: VisualDNA, count: int = 12) -> List[str]:
    """
    生成标题候选列表。
    
    Args:
        user_input: NailNoteUserInput
        visual_dna: VisualDNA
        count: 目标生成数量
    
    Returns:
        标题列表（至少10个）
    """
    brief = getattr(user_input, 'brief', '') or ''
    skin_tone = visual_dna.skin_tone or '黄皮'
    nail_length = visual_dna.nail_length or '短甲'
    nail_shape = visual_dna.nail_shape or '方圆'
    main_color = visual_dna.main_color or ''
    finish = visual_dna.finish or ''
    style = visual_dna.style or ''
    
    client = _get_llm_client()
    
    if client:
        try:
            types_prompt = """标题类型说明：
- 痛点型：解决用户担忧（如"黄皮别怕蓝色"）
- 结果型：强调效果（如"手白一个度"）
- 人群型：锁定目标用户（如"短甲姐妹"）
- 场景型：结合使用场景（如"夏天去海边"）
- 收藏型：促收藏（如"给美甲师看这张就够了"）
- 反差型：制造反差感（如"小小细节大大不同"）
- 细节型：强调细节（如"猫眼光泽绝了"）
- 趋势型：结合热点（如"今夏最火"）
- 轻种草型：温和种草（如"忍不住分享"）
- 转化型：促行动（如"拿图直接冲"）"""

            prompt = f"""{types_prompt}

请为以下美甲款式生成{count}个不同类型的小红书标题：

款式描述：{brief}
肤色：{skin_tone}
甲长：{nail_length}
甲型：{nail_shape}
主色调：{main_color}
质感：{finish}
风格：{style}

要求：
1. 每个标题不超过25字
2. 涵盖痛点型/结果型/人群型/场景型/收藏型/反差型/细节型/趋势型/轻种草型/转化型
3. 标题要吸引眼球，激发点击欲望
4. 包含具体颜色/甲型/效果等关键词

直接返回标题列表，每行一个，用 | 分隔，不要其他文字。
格式：标题1 | 标题2 | 标题3 | ..."""

            response = client.chat.completions.create(
                model=get_text_model("copy_small"),
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.8,
                max_tokens=600,
            )
            text = response.choices[0].message.content.strip()
            
            # 解析
            titles = []
            if '|' in text:
                titles = [t.strip() for t in text.split('|') if t.strip()]
            else:
                # 按换行分割
                titles = [t.strip() for t in text.split('\n') if t.strip()]
            
            if len(titles) >= 10:
                return titles[:count]
        except Exception as e:
            print(f"[title_generator] LLM生成失败: {e}")
    
    # Fallback: 规则生成
    return _generate_titles_fallback(brief, skin_tone, nail_length, main_color, finish, style)


def _generate_titles_fallback(brief: str, skin_tone: str, nail_length: str,
                              main_color: str, finish: str, style: str) -> List[str]:
    """规则生成标题（Fallback）"""
    titles = [
        f"{skin_tone}别怕{main_color}！这款{nail_length}真的显白",
        f"做完手白一个度的{main_color}{nail_length}",
        f"{nail_length}姐妹一定要试试这款",
        f"夏天去海边就做这款{main_color}{finish}",
        f"给美甲师看这张就够了",
        f"{skin_tone}显白神器！{main_color}{nail_length}",
        f"清透{main_color}猫眼，{nail_length}的心动之选",
        f"这款{main_color}{finish}{nail_length}美哭了",
        f"夏日美甲 | {main_color}{nail_length}清单",
        f"简约不简单，{main_color}{nail_length}美甲参考",
        f"被问爆的{main_color}美甲，{nail_length}冲",
        f"{nail_length}美甲模板 | {skin_tone}闭眼入",
    ]
    return titles
