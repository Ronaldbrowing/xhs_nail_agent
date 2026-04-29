"""
笔记图片生成器 - 为笔记的每一页生成图片
调用 orchestrator_v2.run() 生成单页图片，然后移动到笔记输出目录
"""
import os
import shutil
from pathlib import Path
from typing import List
from .note_workflow_schemas import NailNotePackage, NailNoteUserInput, NotePageSpec


def _get_note_output_dir(package: NailNotePackage) -> Path:
    """获取笔记输出目录（绝对路径）"""
    from project_paths import PROJECT_ROOT
    if package.output_dir:
        out = Path(package.output_dir)
        if out.is_absolute():
            return out
        return PROJECT_ROOT / out
    return PROJECT_ROOT / "output" / package.note_id


def _copy_image_to_note_dir(src_path: str, page: NotePageSpec, note_dir: Path) -> str:
    """
    将生成的图片复制到笔记目录，并重命名为 page_XX_role.png。
    
    Returns:
        相对路径（项目相对路径）
    """
    from project_paths import to_project_relative
    
    src = Path(src_path)
    if not src.exists():
        return src_path
    
    # 构建目标文件名
    role_name = page.role.value if hasattr(page.role, 'value') else str(page.role)
    dest_name = f"page_{page.page_no:02d}_{role_name}.png"
    dest = note_dir / dest_name
    
    # 复制文件
    shutil.copy2(src, dest)
    
    # 返回相对路径
    return to_project_relative(str(dest))


def _generate_single_page(
    page: NotePageSpec,
    user_input: NailNoteUserInput,
    note_dir: Path,
) -> NotePageSpec:
    """
    为单页生成图片。
    
    流程：
    1. 调用 orchestrator_v2.run() 生成图片
    2. 复制图片到笔记输出目录
    3. 更新 page 的 image_path 和 status
    """
    from orchestrator_v2 import run
    
    if not page.prompt:
        page.status = "failed"
        page.issues.append("No prompt available")
        return page
    
    try:
        # 调用 orchestrator_v2.run() 生成图片
        task = "poster"
        direction = getattr(user_input, 'direction', 'balanced') or 'balanced'
        aspect = getattr(user_input, 'aspect', '3:4') or '3:4'
        quality = getattr(user_input, 'quality', 'final') or 'final'
        
        result = run(
            user_input=page.prompt,
            use_reference=False,  # note_workflow 自己管理参考图
            task=task,
            direction=direction,
            aspect=aspect,
            quality=quality,
            precompiled_brief=True,
        )
        
        # 提取图片路径
        if isinstance(result, dict):
            filepath = result.get("filepath") or result.get("image_path") or result.get("path")
        else:
            filepath = None
        
        if filepath and Path(filepath).exists():
            # 复制到笔记目录
            rel_path = _copy_image_to_note_dir(filepath, page, note_dir)
            page.image_path = rel_path
            page.status = "generated"
        else:
            page.status = "failed"
            page.issues.append(f"No valid filepath returned: {result}")
            
    except Exception as e:
        page.status = "failed"
        page.issues.append(str(e))
    
    return page


def generate_note_images(
    package: NailNotePackage,
    user_input: NailNoteUserInput,
) -> NailNotePackage:
    """
    为笔记的所有页面生成图片。
    
    按顺序生成，封面失败则整个 package 标记为部分失败。
    
    Args:
        package: NailNotePackage（会被原地修改）
        user_input: NailNoteUserInput
    
    Returns:
        修改后的 package
    """
    note_dir = _get_note_output_dir(package)
    note_dir.mkdir(parents=True, exist_ok=True)
    
    for page in package.pages:
        role_name = page.role.value if hasattr(page.role, 'value') else page.role
        print(f"[图片生成] 🖼️ page_{page.page_no}_{role_name}...")
        
        page = _generate_single_page(page, user_input, note_dir)
        
        if page.status == "generated":
            print(f"[图片生成] ✅ page_{page.page_no}_{role_name} -> {page.image_path}")
        else:
            print(f"[图片生成] ❌ page_{page.page_no}_{role_name} failed: {', '.join(page.issues)}")
            if page.page_no == 1:
                # 封面失败
                package.partial_failure = True
                package.diagnostics["failed_reason"] = "cover_generation_failed"
            else:
                package.partial_failure = True
    
    return package
