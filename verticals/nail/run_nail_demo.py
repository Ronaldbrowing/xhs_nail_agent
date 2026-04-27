import json
from verticals.nail.schemas import UserInput
from verticals.nail.nail_workflow import NailWorkflow
from verticals.nail.style_registry import list_styles

def print_json(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=lambda item: item.__dict__))

def demo_prepare_only():
    workflow = NailWorkflow()
    user_input = UserInput(
        brief="做一篇适合小红书的夏日蓝色猫眼短甲种草笔记，适合黄皮，清透显白",
        style_id="single_seed_summer_cat_eye_short",
        skin_tone="黄皮",
        nail_length="短甲",
        allow_text_on_image=False
    )
    result = workflow.prepare(user_input)
    print_json(result["preview"])

if __name__ == "__main__":
    print("Available nail styles:")
    print_json(list_styles())
    print("")
    print("Demo preview:")
    demo_prepare_only()
