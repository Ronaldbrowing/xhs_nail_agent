#!/usr/bin/env python3
"""
📚 案例库系统 (Case Library)
=======================
功能：
1. 保存生成的图片到案例库（按任务类型分类）
2. 列出案例库中的所有案例
3. 选择案例作为参考图，进行风格迁移（图生图）
4. 支持案例打标签、评分、搜索

案例库路径：<PROJECT_ROOT>/case_library/
├── poster/
│   ├── case_001_xxx/
│   │   ├── image.png
│   │   └── metadata.json
│   └── case_002_xxx/
│       ├── image.png
│       └── metadata.json
├── product/
├── ppt/
├── infographic/
└── teaching/
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

from project_paths import CASE_LIBRARY_DIR, to_project_relative, resolve_project_path


def ensure_dirs():
    CASE_LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    for task in ["poster", "product", "ppt", "infographic", "teaching"]:
        (CASE_LIBRARY_DIR / task).mkdir(exist_ok=True)


ensure_dirs()


def log(msg):
    print(f"[案例库] {msg}")


def add_case(image_path: str, metadata: dict, task: str = "poster", tags: list = None) -> str:
    """
    添加案例到案例库

    Args:
        image_path: 图片路径
        metadata: 元数据（包含 prompt、params 等）
        task: 任务类型
        tags: 标签列表

    Returns:
        案例 ID
    """
    task_dir = CASE_LIBRARY_DIR / task

    # Generate case number
    existing = [d for d in task_dir.iterdir() if d.is_dir()]
    case_num = len(existing) + 1
    case_id = f"case_{case_num:03d}"

    # Create case directory
    case_dir = task_dir / f"{case_id}_{metadata.get('brief', 'untitled')[:20]}"
    case_dir.mkdir(exist_ok=True)

    # Copy image
    ext = Path(image_path).suffix or ".png"
    target_image = case_dir / f"image{ext}"

    # Resolve absolute path before copying
    src_path = resolve_project_path(image_path)
    shutil.copy2(src_path, target_image)

    # Save metadata with relative image_path
    case_meta = {
        "case_id": case_id,
        "task": task,
        "created_at": datetime.now().isoformat(),
        "image_path": to_project_relative(target_image),
        "brief": metadata.get("brief", ""),
        "prompt": metadata.get("prompt", ""),
        "params": metadata.get("params", {}),
        "tags": tags or [],
        "rating": metadata.get("rating", 0),
    }

    with open(case_dir / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(case_meta, f, indent=2, ensure_ascii=False)

    log(f"✅ 案例已保存: {case_dir.name}")
    return case_id


def list_cases(task: str = None) -> list:
    """
    列出案例库中的所有案例

    Args:
        task: 按任务类型过滤 (poster/product/ppt/infographic/teaching)
              None = 显示全部

    Returns:
        案例列表
    """
    cases = []

    tasks_to_list = [task] if task else ["poster", "product", "ppt", "infographic", "teaching"]

    for t in tasks_to_list:
        task_dir = CASE_LIBRARY_DIR / t
        if not task_dir.exists():
            continue

        for case_dir in sorted(task_dir.iterdir()):
            if not case_dir.is_dir():
                continue

            meta_file = case_dir / "metadata.json"
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                cases.append(meta)

    return cases


def search_cases(keyword: str, task: str = None) -> list:
    """搜索案例（按关键词匹配 brief、prompt、tags）"""
    all_cases = list_cases(task)
    keyword_lower = keyword.lower()

    results = []
    for case in all_cases:
        text_to_search = " ".join([
            case.get("brief", ""),
            case.get("prompt", ""),
            " ".join(case.get("tags", []))
        ]).lower()

        if keyword_lower in text_to_search:
            results.append(case)

    return results


def get_case_image_path(case_id: str, task: str = None) -> str:
    """
    获取案例图片路径（返回项目相对路径）

    Args:
        case_id: 案例编号 (如 "case_001")
        task: 任务类型（如果知道）

    Returns:
        图片路径（项目相对路径），找不到返回 None
    """
    if task:
        task_dirs = [CASE_LIBRARY_DIR / task]
    else:
        task_dirs = [CASE_LIBRARY_DIR / t for t in ["poster", "product", "ppt", "infographic", "teaching"]]

    for task_dir in task_dirs:
        if not task_dir.exists():
            continue
        for case_dir in task_dir.iterdir():
            if case_dir.name.startswith(case_id):
                # Look for image file directly in case directory
                for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                    img = case_dir / f"image{ext}"
                    if img.exists():
                        # Clean path - remove any newline characters
                        rel = to_project_relative(img)
                        if "\n" in rel or "\\n" in rel:
                            cleaned_dir = case_dir.name.replace("\n", "").replace("\\n", "").strip()
                            rel = f"case_library/{task_dir.name}/{cleaned_dir}/image{ext}"
                        return rel
    return None


def get_case_metadata(case_id: str, task: str = None) -> dict:
    """
    获取案例元数据

    Args:
        case_id: 案例编号，例如 "case_001"
        task: 任务类型。如果已知任务类型，则只在该任务目录下查找。

    Returns:
        metadata.json 的内容；找不到则返回 None。
    """
    if task:
        task_dirs = [CASE_LIBRARY_DIR / task]
    else:
        task_dirs = [
            CASE_LIBRARY_DIR / t
            for t in ["poster", "product", "ppt", "infographic", "teaching"]
        ]

    for task_dir in task_dirs:
        if not task_dir.exists():
            continue

        for case_dir in task_dir.iterdir():
            if not case_dir.is_dir():
                continue

            if case_dir.name.startswith(case_id):
                meta_file = case_dir / "metadata.json"
                if not meta_file.exists():
                    return None

                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)

                # If image_path in metadata is old absolute path that doesn't exist,
                # but local image.png exists, prefer the local image.png
                stored_image_path = meta.get("image_path")
                if stored_image_path:
                    resolved = resolve_project_path(stored_image_path)
                    if not resolved.exists():
                        # Try local image.png in same dir as fallback
                        local_img = case_dir / "image.png"
                        if local_img.exists():
                            meta["image_path"] = to_project_relative(local_img)
                        else:
                            local_img = case_dir / "image.jpg"
                            if local_img.exists():
                                meta["image_path"] = to_project_relative(local_img)
                            else:
                                local_img = case_dir / "image.jpeg"
                                if local_img.exists():
                                    meta["image_path"] = to_project_relative(local_img)
                                else:
                                    local_img = case_dir / "image.webp"
                                    if local_img.exists():
                                        meta["image_path"] = to_project_relative(local_img)

                return meta

    return None


def print_case_list(cases: list):
    """打印案例列表（美观格式）"""
    if not cases:
        print("   (暂无案例)")
        return

    for case in cases:
        case_id = case.get("case_id", "N/A")
        brief = case.get("brief", "无标题")[:30]
        task = case.get("task", "unknown")
        rating = case.get("rating", 0)
        tags = ", ".join(case.get("tags", [])[:3])
        stars = "⭐" * int(rating) if rating else ""

        print(f"   {case_id} [{task}] {brief} {stars}")
        if tags:
            print(f"      🏷️  {tags}")


def interactive_select_case(task: str = None) -> str:
    """
    交互式选择案例

    Returns:
        选中的案例图片路径，或 None（不选择）
    """
    print("\n" + "=" * 60)
    print("📚 案例库")
    print("=" * 60)

    cases = list_cases(task)

    if not cases:
        print("\n案例库为空，直接生成新图片。\n")
        return None

    print(f"\n找到 {len(cases)} 个案例:\n")
    print_case_list(cases)

    print("\n选项:")
    print("  [1-N] 选择案例编号参考")
    print("  [s]   搜索案例")
    print("  [n]   不参考案例，直接生成")
    print()

    choice = input("你的选择: ").strip().lower()

    if choice == 'n' or not choice:
        print("   → 不参考案例\n")
        return None

    if choice == 's':
        keyword = input("搜索关键词: ").strip()
        results = search_cases(keyword, task)
        if results:
            print(f"\n搜索结果 ({len(results)} 个):")
            print_case_list(results)
            idx = input("选择编号 (1-N): ").strip()
            try:
                selected = results[int(idx) - 1]
                return selected["image_path"]
            except:
                print("   → 无效选择，不参考案例\n")
                return None
        else:
            print("   → 未找到匹配案例\n")
            return None

    # Select by number
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(cases):
            selected = cases[idx]
            print(f"   → 已选择: {selected['case_id']} - {selected['brief'][:30]}\n")
            return selected["image_path"]
    except:
        pass

    print("   → 无效选择，不参考案例\n")
    return None


def auto_save_to_library(generation_result: dict, brief: str, params: dict):
    """自动生成完成后，自动保存到案例库"""
    if generation_result.get("status") != "success":
        return

    filepath = generation_result.get("filepath")
    if not filepath:
        return

    # Resolve to absolute path before saving
    abs_path = resolve_project_path(filepath)
    if not abs_path.exists():
        return

    metadata = {
        "brief": brief,
        "prompt": generation_result.get("final_prompt", ""),
        "params": params,
        "rating": 0,
    }

    task = params.get("task", "poster")
    add_case(str(abs_path), metadata, task=task)


# Shortcut commands
def lib():
    """查看案例库"""
    print("\n📚 案例库概览:\n")
    for task in ["poster", "product", "ppt", "infographic", "teaching"]:
        cases = list_cases(task)
        print(f"【{task}】({len(cases)} 个)")
        print_case_list(cases)
        print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "list":
            lib()
        elif cmd == "search" and len(sys.argv) > 2:
            results = search_cases(sys.argv[2])
            print_case_list(results)
        else:
            print("用法: python case_library.py [list|search <关键词>]")
    else:
        lib()
