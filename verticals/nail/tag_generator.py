"""
TAG生成器 - 生成15-25个TAG
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


def generate_tags(user_input, visual_dna: VisualDNA, count: int = 20) -> List[str]:
    """
    生成TAG列表。
    
    Args:
        user_input: NailNoteUserInput
        visual_dna: VisualDNA
        count: 目标数量（15-25）
    
    Returns:
        TAG列表
    """
    brief = getattr(user_input, 'brief', '') or ''
    skin_tone = visual_dna.skin_tone or '黄皮'
    nail_length = visual_dna.nail_length or '短甲'
    nail_shape = visual_dna.nail_shape or '方圆'
    main_color = visual_dna.main_color or '清透色'
    finish = visual_dna.finish or ''
    style = visual_dna.style or ''

    client = _get_llm_client()

    if client:
        try:
            prompt = f"""为以下小红书美甲款式生成{count}个标签（TAG）：

款式：{brief}
肤色：{skin_tone}
甲长：{nail_length}
甲型：{nail_shape}
主色调：{main_color}
质感：{finish}
风格：{style}

要求：
1. 生成{count}个标签
2. 包括：通用美甲标签、颜色标签、甲型标签、场景标签、肤色相关标签、人群标签
3. 每个标签2-8字
4. 不要重复
5. 必须包含以下类型：
   - 通用：美甲、美甲款式、美甲参考、美甲灵感
   - 颜色：实际颜色名（如蓝色、粉色）不要只写"蓝色美甲"
   - 甲型：{nail_length}、{nail_shape}
   - 肤色：{skin_tone}相关
   - 场景：夏日、海边、约会、通勤等
   - 人群：适合人群标签

直接返回标签列表，每行一个，用 | 分隔，不要其他文字。
格式：美甲 | 夏日美甲 | ... """

            response = client.chat.completions.create(
                model=get_text_model("tag_small"),
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.5,
                max_tokens=400,
            )
            text = response.choices[0].message.content.strip()
            
            tags = []
            if '|' in text:
                tags = [t.strip() for t in text.split('|') if t.strip()]
            else:
                tags = [t.strip() for t in text.split('\n') if t.strip()]
            
            # 去重
            seen = set()
            unique_tags = []
            for t in tags:
                if t not in seen and len(t) <= 15:
                    seen.add(t)
                    unique_tags.append(t)
            
            if len(unique_tags) >= 15:
                return unique_tags[:count]
        except Exception as e:
            print(f"[tag_generator] LLM生成失败: {e}")

    # Fallback
    return _generate_tags_fallback(skin_tone, nail_length, nail_shape, main_color, finish, style)


def _generate_tags_fallback(skin_tone: str, nail_length: str,
                           nail_shape: str, main_color: str,
                           finish: str, style: str) -> List[str]:
    """规则生成TAG（Fallback）"""
    tags = [
        "美甲", "夏日美甲", "猫眼美甲", f"{main_color}美甲",
        f"{nail_length}美甲", "清透美甲", f"{skin_tone}显白美甲",
        "美甲参考", "给美甲师看", "美甲灵感", "简约美甲",
        "精致美甲", "约会美甲", "通勤美甲", "海边美甲",
        "美甲款式", "显白美甲", "气质美甲", "日常美甲",
        "美甲教程", "美甲分享", "亲手美甲", "美甲控",
    ]
    # 去重
    seen = set()
    unique = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique[:25]
