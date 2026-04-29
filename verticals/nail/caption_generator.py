"""
正文生成器 - 生成完整笔记正文
"""
import os
from typing import List
from .note_workflow_schemas import VisualDNA, NotePageSpec


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


def generate_caption(user_input, visual_dna: VisualDNA, pages: List[NotePageSpec] = None) -> str:
    """
    生成完整正文。
    
    Args:
        user_input: NailNoteUserInput
        visual_dna: VisualDNA
        pages: 页面列表（可选，用于参考页面规划）
    
    Returns:
        正文字符串
    """
    brief = getattr(user_input, 'brief', '') or ''
    skin_tone = visual_dna.skin_tone or '黄皮'
    nail_length = visual_dna.nail_length or '短甲'
    nail_shape = visual_dna.nail_shape or '方圆'
    main_color = visual_dna.main_color or '清透色'
    finish = visual_dna.finish or '质感'
    style = visual_dna.style or '清透显白'

    client = _get_openai_client()

    if client:
        try:
            prompt = f"""为以下小红书美甲款式写一篇完整的笔记正文：

款式：{brief}
肤色：{skin_tone}
甲长：{nail_length}
甲型：{nail_shape}
主色调：{main_color}
质感：{finish}
风格：{style}

要求：
1. 开头钩子：引发好奇或共鸣（如"黄皮姐妹真的可以冲蓝色"）
2. 款式描述：具体描述颜色、质感、适合场景
3. 适合人群：哪些人适合这款
4. 细节亮点：猫眼光泽、甲型、搭配等
5. 避雷建议：哪些人不适合或需要注意的点
6. 给美甲师的复刻关键词：颜色名、质感、甲型、长度
7. 互动结尾：引发评论（如"你们更喜欢短甲还是中长甲"）

正文要有真情实感，不要过于营销化。字数300-500字。

直接返回正文，不要标题，不要其他说明。"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1200,
            )
            text = response.choices[0].message.content.strip()
            if text and len(text) > 100:
                return text
        except Exception as e:
            print(f"[caption_generator] LLM生成失败: {e}")

    # Fallback
    return _generate_caption_fallback(brief, skin_tone, nail_length, nail_shape, main_color, finish, style)


def _generate_caption_fallback(brief: str, skin_tone: str, nail_length: str,
                                nail_shape: str, main_color: str,
                                finish: str, style: str) -> str:
    """规则生成正文（Fallback）"""
    return f"""救命！这款{main_color}{nail_length}美哭了😭

{skin_tone}姐妹真的可以冲！这款{main_color}{finish}的{nail_length}{nail_shape}，上手直接白一个度有没有！

✨ 款式描述
{main_color}为主色调，{finish}质感，{nail_length}{nail_shape}，整体风格{style}。猫眼磁粉在光线下折射出细腻光泽，真的绝！

👩 适合人群
适合{skin_tone}、喜欢{style}风格的姐妹。{nail_length}不挑手型，{nail_shape}显手指纤细。

💅 细节亮点
• 猫眼光泽感绝了，自然光下超美
• {nail_length}{nail_shape}显手白
• {main_color}显肤色通透
• 日常通勤约会都OK

⚠️ 避雷建议
• 白皮姐妹这款可能不够显白
• 喜欢夸张风格的绕道
• 手部较黑的建议先试色

💬 给美甲师的复刻关键词
{main_color}猫眼胶 / {nail_length}{nail_shape} / 玻璃质感封层 / 自然光

你们更喜欢短甲还是中长甲？评论区告诉我呀～

#美甲 #夏日美甲 #{main_color}美甲 #猫眼美甲 #{skin_tone}显白"""
