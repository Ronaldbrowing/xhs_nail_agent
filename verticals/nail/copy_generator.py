import json
from typing import Optional
from .schemas import UserInput, NailStyle, ReferenceDNA

def join_list(items):
    return "、".join([str(x) for x in items if x])

def build_copy_prompt(user_input: UserInput, style: NailStyle, dna: Optional[ReferenceDNA]) -> str:
    tags = []
    for group in ["core_tags", "scene_tags", "element_tags", "skin_tone_tags"]:
        tags.extend(style.tags.get(group, []))

    parts = [
        "请为一篇小红书美甲图文笔记生成爆款文案。",
        "要求像真实小红书用户发布，不要像硬广。",
        f"场景：{style.style_name}",
        f"用户需求：{user_input.brief}",
        f"标题公式：{style.copywriting.get('title_formula', '')}",
        f"开头角度：{style.copywriting.get('opening_angle', '')}",
        f"正文结构：{join_list(style.copywriting.get('body_structure', []))}",
        f"评论区钩子：{join_list(style.copywriting.get('comment_hooks', []))}",
        f"行动引导：{style.copywriting.get('cta', '')}",
        f"可用标签池：{join_list(tags)}"
    ]

    if dna:
        parts.append(f"参考图核心元素：{join_list(dna.main_visual_identity)}")
        parts.append(f"参考图主色：{join_list(dna.dominant_colors)}")
        parts.append(f"参考图质感：{join_list(dna.finish_types)}")
        parts.append(f"参考图装饰：{join_list(dna.decorations)}")

    parts.append("请输出 JSON：titles 为3个标题，bodies 为3篇正文，tags 为3组tag。")
    return "\n".join(parts)

def fallback_copy(user_input: UserInput, style: NailStyle):
    base_tags = []
    for group in ["core_tags", "scene_tags", "element_tags", "skin_tone_tags"]:
        base_tags.extend(style.tags.get(group, []))
    base_tags = base_tags[:10]

    return {
        "titles": [
            "夏日小短甲｜这款真的清透又显白",
            "黄皮也能冲的温柔显白美甲",
            "短甲女孩会反复做的一款美甲"
        ],
        "bodies": [
            "这款属于一眼干净的美甲，重点是显白、清透、不夸张。短甲做出来也不会显手短，日常通勤和拍照都比较友好。色号、价格和适合肤色可以放在评论区继续补充，喜欢的可以先收藏给美甲师看。",
            "如果你担心美甲太复杂、太显黑，可以优先选这种低饱和显白路线。它不靠大面积装饰取胜，而是靠颜色、光泽和手部干净度出效果。短甲、黄皮、日常党都可以参考。",
            "这款适合想要精致但不想太高调的人。整体是小红书上比较容易被收藏的类型：画面干净、款式明确、适合直接拿给美甲师沟通。"
        ],
        "tags": [base_tags, base_tags, base_tags]
    }

def generate_copy(llm_client, user_input: UserInput, style: NailStyle, dna: Optional[ReferenceDNA]):
    prompt = build_copy_prompt(user_input, style, dna)

    if llm_client is None:
        return fallback_copy(user_input, style), prompt

    raw = llm_client.generate(prompt)
    text = raw.strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(text)
    except Exception:
        data = fallback_copy(user_input, style)

    return data, prompt
