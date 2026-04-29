"""
评论钩子生成器 - 生成3-5个引发评论的钩子
"""
import os
from typing import List
from .note_workflow_schemas import VisualDNA


def _get_openai_client():
    try:
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            try:
                from gpt_image2_generator import get_api_key
                api_key = get_api_key()
            except ImportError:
                pass
        if api_key:
            return OpenAI(api_key=api_key)
    except Exception:
        pass
    return None


def generate_comment_hooks(user_input, visual_dna: VisualDNA, count: int = 4) -> List[str]:
    """
    生成评论钩子列表。

    Args:
        user_input: NailNoteUserInput
        visual_dna: VisualDNA
        count: 目标数量（3-5）

    Returns:
        评论钩子列表
    """
    brief = getattr(user_input, 'brief', '') or ''
    skin_tone = visual_dna.skin_tone or '黄皮'
    nail_length = visual_dna.nail_length or '短甲'
    nail_shape = visual_dna.nail_shape or '方圆'
    main_color = visual_dna.main_color or '清透色'
    finish = visual_dna.finish or ''

    client = _get_openai_client()

    if client:
        try:
            prompt = f"""为以下小红书美甲款式生成{count}个评论钩子（引发用户评论互动的问题）：

款式：{brief}
肤色：{skin_tone}
甲长：{nail_length}
甲型：{nail_shape}
主色调：{main_color}
质感：{finish}

要求：
1. 生成{count}个评论钩子
2. 每个钩子是一个问题，能引发用户主动评论
3. 类型不限：可以是选择题、投票、经验分享请求、观点征集等
4. 简短有趣，5-20字
5. 不要太营销化

直接返回钩子列表，每行一个，用 | 分隔，不要其他文字。
格式：钩子1 | 钩子2 | 钩子3 | ..."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300,
            )
            text = response.choices[0].message.content.strip()

            hooks = []
            if '|' in text:
                hooks = [h.strip() for h in text.split('|') if h.strip()]
            else:
                hooks = [h.strip() for h in text.split('\n') if h.strip()]

            if len(hooks) >= 3:
                return hooks[:count]
        except Exception as e:
            print(f"[comment_hook_generator] LLM生成失败: {e}")

    # Fallback
    return _generate_hooks_fallback(skin_tone, nail_length, nail_shape, main_color, finish)


def _generate_hooks_fallback(skin_tone: str, nail_length: str,
                             nail_shape: str, main_color: str,
                             finish: str) -> List[str]:
    """规则生成评论钩子（Fallback）"""
    hooks = [
        f"你们觉得{main_color}美甲更适合{nail_length}还是中长甲？",
        f"{skin_tone}姐妹会不会敢尝试{main_color}？评论区告诉我",
        f"想要我整理一组不显黑的{main_color}美甲吗？",
        f"如果拿去给美甲师看，你会选第几页？",
        f"下一期想看{main_color}显白款还是裸色通勤款？",
    ]
    return hooks
