"""
视觉DNA构建器 - 从用户输入、参考图、案例库构建 VisualDNA
"""
import re
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


def _extract_color_from_brief(brief: str) -> Optional[str]:
    """从 brief 提取颜色"""
    color_patterns = [
        r'([\u4e00-\u9fa5]{1,3}色)', r'(冰[透甲]+)', r'(猫眼)',
        r'(透[明甲]+)', r'(白[嫩透]+)', r'(粉[白嫩]+)', r'(蓝[白透]+)',
        r'(紫[粉]+)', r'(红[棕]+)', r'(橘[粉]+)', r'(裸[色]+)',
    ]
    colors = []
    for pattern in color_patterns:
        matches = re.findall(pattern, brief)
        colors.extend(matches)
    if colors:
        return ' '.join(colors[:3])
    return None


def _extract_style_from_brief(brief: str) -> Optional[str]:
    """从 brief 提取风格"""
    style_keywords = {
        '清透': '清透', '显白': '显白', '日常': '日常', '精致': '精致',
        '简约': '简约', '高级': '高级感', '气质': '气质', '温柔': '温柔',
        '元气': '元气', '轻奢': '轻奢', '复古': '复古', '法式': '法式',
        '日系': '日系', '韩系': '韩系', '欧美': '欧美风',
    }
    found = []
    brief_lower = brief.lower()
    for kw, style in style_keywords.items():
        if kw in brief_lower:
            found.append(style)
    return ' '.join(found) if found else None


def _extract_finish_from_brief(brief: str) -> Optional[str]:
    """从 brief 提取质感"""
    finish_keywords = {
        '猫眼': '猫眼磁粉，玻璃感，高光泽',
        '冰透': '冰透感，清凉，玻璃指甲',
        '镜面': '镜面效果，高光反射',
        '磨砂': '磨砂质感，哑光',
        '砂糖': '砂糖颗粒感',
        '晕染': '晕染渐变',
        '珍珠': '珍珠贝母质感',
        '镭射': '镭射偏光',
        '渐变': '渐变色彩',
    }
    found = []
    brief_lower = brief.lower()
    for kw, finish in finish_keywords.items():
        if kw in brief_lower:
            found.append(finish)
    return ' '.join(found) if found else None


def _extract_nail_shape_from_brief(brief: str) -> Optional[str]:
    """从 brief 提取甲型"""
    shape_keywords = {
        '方圆': '短方圆', '方圓': '短方圆',
        '杏仁': '杏仁形', '尖形': '尖形', '尖圆': '尖圆形',
        '方': '方形', '圓': '圆形', '椭圆': '椭圆形',
    }
    for kw, shape in shape_keywords.items():
        if kw in brief:
            return shape
    return None


def _extract_nail_length_from_brief(brief: str) -> Optional[str]:
    """从 brief 提取甲长"""
    length_keywords = {
        '超短': '超短甲', '短甲': '短甲', '短': '短甲',
        '中长': '中长甲', '中长': '中长甲', '长': '长甲',
    }
    for kw, length in length_keywords.items():
        if kw in brief:
            return length
    return None


def _get_default_negative(skin_tone: str = None, nail_shape: str = None) -> list:
    """获取默认负面清单"""
    negatives = [
        "长尖甲", "暗沉灰蓝", "欧美夸张风", "廉价闪粉",
        "过度磨皮", "多余手指", "畸形手部", "指甲过长",
        "背景杂乱", "水印文字", "手指关节突兀",
    ]
    if nail_shape:
        if '短' in nail_shape:
            negatives.extend(["长尖甲", "指甲过长"])
        elif '长' in nail_shape:
            negatives.extend(["短甲", "过短"])
    return list(set(negatives))


def _build_dna_from_llm(brief: str, skin_tone: str = None, nail_length: str = None,
                        nail_shape: str = None, style_id: str = None) -> VisualDNA:
    """用 LLM 从 brief 推断 VisualDNA"""
    client = _get_llm_client()
    
    prompt = f"""根据以下美甲需求，提取视觉DNA信息。

需求描述：{brief}
肤色：{skin_tone or '未指定'}
甲长：{nail_length or '未指定'}
甲型：{nail_shape or '未指定'}
风格ID：{style_id or '未指定'}

请提取以下信息并返回JSON格式：
- skin_tone: 肤色描述（如：黄皮/白皮/黑皮）
- hand_model: 手型描述（如：自然亚洲女性手型）
- nail_length: 甲长（如：短甲/中长甲/长甲）
- nail_shape: 甲型（如：短方圆/杏仁/尖形）
- main_color: 主色调（从brief中提取具体颜色）
- finish: 质感（猫眼/冰透/镜面/磨砂等）
- lighting: 光线描述
- background: 背景描述
- style: 整体风格（清透/显白/日常/精致等）
- negative: 负面清单（需要避免的元素）

只返回JSON，不要其他文字。"""

    try:
        if client:
            response = client.chat.completions.create(
                model=get_text_model("vision_small"),
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.3,
                max_tokens=500,
            )
            text = response.choices[0].message.content.strip()
            # 提取 JSON
            if '{' in text:
                json_str = text[text.find('{'):text.rfind('}')+1]
                import json
                data = json.loads(json_str)
                return VisualDNA(
                    skin_tone=data.get('skin_tone'),
                    hand_model=data.get('hand_model', '自然亚洲女性手型'),
                    nail_length=data.get('nail_length') or nail_length,
                    nail_shape=data.get('nail_shape') or nail_shape,
                    main_color=data.get('main_color'),
                    finish=data.get('finish'),
                    lighting=data.get('lighting', '自然光，柔和明亮'),
                    background=data.get('background', '干净浅色背景，小红书风格'),
                    style=data.get('style'),
                    negative=data.get('negative', []),
                )
    except Exception:
        pass
    
    # Fallback: 规则推断
    return _build_dna_from_rules(brief, skin_tone, nail_length, nail_shape)


def _build_dna_from_rules(brief: str, skin_tone: str = None, nail_length: str = None,
                          nail_shape: str = None) -> VisualDNA:
    """用规则从 brief 推断 VisualDNA"""
    return VisualDNA(
        skin_tone=skin_tone,
        hand_model="自然亚洲女性手型",
        nail_length=nail_length or _extract_nail_length_from_brief(brief) or "短甲",
        nail_shape=nail_shape or _extract_nail_shape_from_brief(brief) or "短方圆",
        main_color=_extract_color_from_brief(brief) or "清透色",
        finish=_extract_finish_from_brief(brief) or "清透质感",
        lighting="自然光，柔和明亮",
        background="干净浅色背景，小红书风格",
        style=_extract_style_from_brief(brief) or "清透、显白、日常",
        negative=_get_default_negative(skin_tone, nail_shape),
    )


def build_visual_dna(user_input, reference_image_path: str = None,
                     case_id: str = None) -> VisualDNA:
    """
    从用户输入构建 VisualDNA。
    
    优先级：reference_image_path > case_id > brief 推断
    
    Args:
        user_input: NailNoteUserInput 或 UserInput
        reference_image_path: 参考图路径
        case_id: 案例ID
    
    Returns:
        VisualDNA 对象
    """
    brief = getattr(user_input, 'brief', '') or ''
    skin_tone = getattr(user_input, 'skin_tone', None) or None
    nail_length = getattr(user_input, 'nail_length', None) or None
    nail_shape = getattr(user_input, 'nail_shape', None) or None
    style_id = getattr(user_input, 'style_id', None) or None
    
    # 1. 有参考图时，从参考图提取
    if reference_image_path:
        try:
            # 尝试用 vision 分析参考图
            from project_paths import resolve_project_path
            img_path = resolve_project_path(reference_image_path)
            if img_path.exists():
                from .vision_analyze_helper import analyze_image_for_dna
                dna = analyze_image_for_dna(str(img_path))
                if dna:
                    dna.source_reference = str(reference_image_path)
                    return dna
        except Exception:
            pass
    
    # 2. 有 case_id 时，从案例库加载
    if case_id:
        try:
            from .case_dna_loader import load_dna_from_case
            dna = load_dna_from_case(case_id)
            if dna:
                dna.source_reference = f"case_id:{case_id}"
                return dna
        except Exception:
            pass
    
    # 3. 从 brief + 字段推断
    return _build_dna_from_llm(brief, skin_tone, nail_length, nail_shape, style_id)
