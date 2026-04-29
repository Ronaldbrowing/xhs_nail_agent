"""
笔记包写入器 - 保存 note_package.json 和 archive.json
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from .note_workflow_schemas import NailNotePackage, model_to_dict


def _sanitize_path(path: str) -> str:
    """清理路径中的多余字符"""
    if not path:
        return path
    # 移除协议前缀
    path = path.replace("file://", "")
    return path.strip()


def _relative_path_for_json(abs_path: str, project_root: Path) -> str:
    """
    将绝对路径转换为相对于项目根目录的相对路径。
    用于写入 JSON 时确保路径是项目相对路径。
    """
    try:
        p = Path(abs_path).resolve()
        if p.is_relative_to(project_root):
            return str(p.relative_to(project_root))
        # 如果不是 relative to，尝试直接返回原始字符串
        return str(abs_path)
    except Exception:
        return str(abs_path)


def _serialize_for_json(obj, project_root: Path) -> dict:
    """
    序列化对象用于 JSON 写入。
    - Pydantic models -> dict
    - enums -> value
    - Path -> relative string
    """
    if isinstance(obj, dict):
        return {k: _serialize_for_json(v, project_root) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_for_json(item, project_root) for item in obj]
    elif isinstance(obj, (Path, os.PathLike)):
        return _relative_path_for_json(str(obj), project_root)
    elif hasattr(obj, 'value'):
        # Enum
        return obj.value
    elif hasattr(obj, 'model_dump'):
        # Pydantic v2
        return _serialize_for_json(obj.model_dump(), project_root)
    elif hasattr(obj, 'dict'):
        # Pydantic v1
        return _serialize_for_json(obj.dict(), project_root)
    else:
        return obj


def write_note_package(package: NailNotePackage, output_dir: str) -> bool:
    """
    保存 NailNotePackage 到 note_package.json 和 archive.json。
    
    Args:
        package: NailNotePackage
        output_dir: 输出目录（相对路径或绝对路径）
    
    Returns:
        True 成功，False 失败
    """
    try:
        from project_paths import PROJECT_ROOT, to_project_relative
        
        # 确保输出目录存在
        if Path(output_dir).is_absolute():
            out_path = Path(output_dir)
        else:
            out_path = PROJECT_ROOT / output_dir
        
        out_path.mkdir(parents=True, exist_ok=True)

        # 先更新路径（确保序列化时包含正确值）
        pkg_path = out_path / "note_package.json"
        arch_path = out_path / "archive.json"
        package.package_path = to_project_relative(str(pkg_path))
        package.archive_path = to_project_relative(str(arch_path))
        package.output_dir = to_project_relative(str(out_path))

        # 序列化 package（路径更新后）
        data = _serialize_for_json(package, PROJECT_ROOT)
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 写入 archive.json（额外元数据）
        archive_data = {
            "generated_at": datetime.now().isoformat(),
            "package_version": "1.0",
            "note_id": package.note_id,
            "brief": package.brief,
            "note_goal": package.note_goal.value if hasattr(package.note_goal, 'value') else str(package.note_goal),
            "page_count": len(package.pages),
            "pages_summary": [
                {
                    "page_no": p.page_no,
                    "role": p.role.value if hasattr(p.role, 'value') else str(p.role),
                    "status": p.status,
                    "image_path": p.image_path,
                }
                for p in package.pages
            ],
            "success": package.success,
            "partial_failure": package.partial_failure,
            "diagnostics": package.diagnostics,
        }
        
        arch_path = out_path / "archive.json"
        with open(arch_path, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        print(f"[package_writer] 保存失败: {e}")
        package.diagnostics["package_write_error"] = str(e)
        return False
