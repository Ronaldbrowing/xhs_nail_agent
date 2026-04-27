import json
from pathlib import Path
from typing import Dict
from .schemas import NailStyle

STYLE_DIR = Path(__file__).parent / "styles"

def load_style_file(path: Path) -> NailStyle:
    data = json.loads(path.read_text(encoding="utf-8"))
    return NailStyle(**data)

def load_all_styles() -> Dict[str, NailStyle]:
    styles = {}
    for path in STYLE_DIR.glob("*.json"):
        style = load_style_file(path)
        styles[style.style_id] = style
    return styles

def get_style(style_id: str) -> NailStyle:
    styles = load_all_styles()
    if style_id not in styles:
        raise KeyError(f"Unknown nail style_id: {style_id}")
    return styles[style_id]

def list_styles():
    return [
        {
            "style_id": s.style_id,
            "style_name": s.style_name,
            "scene_type": s.scene_type,
            "task": s.task,
            "direction": s.direction,
            "aspect": s.aspect
        }
        for s in load_all_styles().values()
    ]
