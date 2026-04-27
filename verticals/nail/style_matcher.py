from .schemas import UserInput, NailStyle
from .style_registry import load_all_styles

def match_style(user_input: UserInput) -> NailStyle:
    styles = load_all_styles()
    if not styles:
        raise RuntimeError("No style json files found in verticals/nail/styles")

    if user_input.style_id and user_input.style_id in styles:
        return styles[user_input.style_id]

    text = " ".join([user_input.brief or "", user_input.scene_hint or "", user_input.note_goal or ""])

    rules = [
        ("collection_cover_6_grid_whitening", ["合集", "6款", "六款", "多款", "收藏给美甲师"]),
        ("tutorial_diy_step_by_step", ["教程", "步骤", "怎么做", "DIY", "手残党", "新手"]),
        ("warning_before_after_nail_fail", ["避雷", "翻车", "踩坑", "千万别", "显黑", "做前必看"]),
        ("comparison_color_skin_tone_test", ["对比", "测评", "横评", "哪个更", "显白对比", "色号"]),
        ("story_mood_date_travel_nail", ["约会", "旅行", "氛围", "拍照", "咖啡", "海边", "故事"]),
        ("trend_fast_follow_from_viral", ["爆款", "同款", "复刻", "趋势", "最近刷到", "跟款"])
    ]

    for style_id, keywords in rules:
        if style_id in styles and any(k in text for k in keywords):
            return styles[style_id]

    return styles.get("single_seed_summer_cat_eye_short") or list(styles.values())[0]
