import json
from .schemas import ReferenceDNA

DNA_EXTRACTION_PROMPT = """
你是一个小红书美甲图片分析助手。
请分析参考图，提取适合美甲图文封面生成的视觉 DNA。
只输出 JSON，不要输出解释。
字段：subject, hand_model, nail_shape, nail_length, dominant_colors, finish_types, decorations, composition, background, lighting, mood, title_area_hint, main_visual_identity
"""

def safe_json_loads(raw: str):
    text = raw.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)

def extract_dna_from_model(image_path: str, multimodal_client=None) -> ReferenceDNA:
    if multimodal_client is None:
        return ReferenceDNA(
            subject="参考图已上传，但当前没有配置多模态分析客户端",
            main_visual_identity=["需接入多模态模型后自动提取 DNA"]
        )

    raw = multimodal_client.analyze_image(image_path=image_path, prompt=DNA_EXTRACTION_PROMPT)
    data = safe_json_loads(raw)

    return ReferenceDNA(
        subject=data.get("subject", ""),
        hand_model=data.get("hand_model", ""),
        nail_shape=data.get("nail_shape", ""),
        nail_length=data.get("nail_length", ""),
        dominant_colors=data.get("dominant_colors", []),
        finish_types=data.get("finish_types", []),
        decorations=data.get("decorations", []),
        composition=data.get("composition", ""),
        background=data.get("background", ""),
        lighting=data.get("lighting", ""),
        mood=data.get("mood", ""),
        title_area_hint=data.get("title_area_hint", ""),
        main_visual_identity=data.get("main_visual_identity", [])
    )
