"""
案例库DNA加载器 - 从 case_library 加载预设的 VisualDNA
"""
import os
import json
from typing import Optional
from .note_workflow_schemas import VisualDNA


def _find_case_dir(case_id: str) -> Optional[str]:
    """找到案例目录"""
    try:
        from project_paths import PROJECT_ROOT
        case_library = PROJECT_ROOT / "case_library"
        if not case_library.exists():
            return None
        
        # 遍历所有 task 子目录
        for task_dir in case_library.iterdir():
            if not task_dir.is_dir():
                continue
            # 查找匹配的 case_id 目录
            for item in task_dir.iterdir():
                if item.is_dir() and case_id in item.name:
                    return str(item)
                # 也检查是否有 metadata.json
                meta_file = item / "metadata.json"
                if meta_file.exists():
                    try:
                        meta = json.loads(meta_file.read_text(encoding="utf-8"))
                        if meta.get("case_id") == case_id or meta.get("id") == case_id:
                            return str(item)
                    except Exception:
                        pass
    except Exception:
        pass
    return None


def load_dna_from_case(case_id: str) -> Optional[VisualDNA]:
    """
    从案例库加载预设的 VisualDNA。
    
    查找 case_library/*/case_id_xxx/ 目录下的 metadata.json，
    尝试从中读取 DNA 信息。
    """
    case_dir = _find_case_dir(case_id)
    if not case_dir:
        return None
    
    # 尝试读取 metadata.json
    meta_path = os.path.join(case_dir, "metadata.json")
    if os.path.exists(meta_path):
        try:
            meta = json.loads(open(meta_path, encoding="utf-8").read())
            
            # 尝试从 metadata 提取 DNA
            visual = meta.get("visual", {}) or {}
            dna_data = meta.get("dna", {}) or {}
            
            if dna_data:
                return VisualDNA(
                    skin_tone=dna_data.get("skin_tone"),
                    hand_model=dna_data.get("hand_model"),
                    nail_length=dna_data.get("nail_length"),
                    nail_shape=dna_data.get("nail_shape"),
                    main_color=dna_data.get("main_color"),
                    finish=dna_data.get("finish"),
                    lighting=dna_data.get("lighting"),
                    background=dna_data.get("background"),
                    style=dna_data.get("style"),
                    negative=dna_data.get("negative", []),
                )
            
            # 也尝试从 visual 字段提取
            if visual:
                return VisualDNA(
                    skin_tone=visual.get("skin_tone"),
                    hand_model=visual.get("hand_model"),
                    nail_length=visual.get("nail_length"),
                    nail_shape=visual.get("nail_shape"),
                    main_color=visual.get("dominant_colors", [None])[0] if visual.get("dominant_colors") else None,
                    finish=', '.join(visual.get("finish_types", [])) if visual.get("finish_types") else None,
                    lighting=visual.get("lighting"),
                    background=visual.get("background"),
                    style=visual.get("mood"),
                    negative=[],
                )
        except Exception:
            pass
    
    return None
