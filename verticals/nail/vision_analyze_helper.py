"""
视觉分析辅助 - 从参考图提取 VisualDNA
"""
from typing import Optional
from .note_workflow_schemas import VisualDNA
from src.llm_provider import get_text_client, get_text_model


def _get_llm_client():
    """获取 OpenAI-compatible client"""
    try:
        return get_text_client()
    except Exception:
        pass
    return None


def analyze_image_for_dna(image_path: str) -> Optional[VisualDNA]:
    """
    用 vision API 分析参考图，提取 VisualDNA。
    
    Args:
        image_path: 图片路径（绝对路径）
    
    Returns:
        VisualDNA 对象，或 None（分析失败时）
    """
    client = _get_llm_client()
    if not client:
        return None
    
    prompt = """分析这张美甲图片，提取视觉DNA信息。

请详细描述：
1. 肤色：手部模特的肤色（黄皮/白皮/黑皮/自然色）
2. 手型：手型特征（纤细/匀称/肉感）
3. 甲长：指甲长度（短甲/中长甲/长甲）
4. 甲型：指甲形状（短方圆/杏仁/尖形/方形/椭圆形）
5. 主色调：主要颜色（具体颜色名称+质感描述）
6. 质感：表面质感（猫眼/冰透/镜面/磨砂/亮面/哑光/砂糖/晕染）
7. 光线：整体光线（自然光/暖光/冷光/柔光/强光）
8. 背景：背景描述（纯色/渐变/场景/杂乱）
9. 风格：整体风格（清透/显白/日常/精致/高级/气质/温柔）

请返回JSON格式：
{
    "skin_tone": "描述",
    "hand_model": "描述",
    "nail_length": "短甲/中长甲/长甲",
    "nail_shape": "甲型",
    "main_color": "主色调+质感",
    "finish": "质感",
    "lighting": "光线",
    "background": "背景",
    "style": "风格",
    "negative": ["避免的元素"]
}

只返回JSON。"""

    try:
        response = client.chat.completions.create(
            model=get_text_model("vision_small"),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"file://{image_path}"}},
                        {"type": "text", "text": prompt}
                    ]
                }
            ],
            stream=False,
            max_tokens=800,
        )
        text = response.choices[0].message.content.strip()
        if '{' in text and '}' in text:
            json_str = text[text.find('{'):text.rfind('}')+1]
            import json
            data = json.loads(json_str)
            return VisualDNA(
                skin_tone=data.get('skin_tone'),
                hand_model=data.get('hand_model', '自然亚洲女性手型'),
                nail_length=data.get('nail_length'),
                nail_shape=data.get('nail_shape'),
                main_color=data.get('main_color'),
                finish=data.get('finish'),
                lighting=data.get('lighting', '自然光'),
                background=data.get('background'),
                style=data.get('style'),
                negative=data.get('negative', []),
            )
    except Exception as e:
        print(f"[vision_analyze_helper] 分析失败: {e}")
    
    return None
