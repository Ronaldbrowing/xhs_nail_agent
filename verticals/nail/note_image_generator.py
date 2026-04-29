"""
笔记图片生成器 - 为笔记的每一页生成图片
调用 orchestrator_v2.run() 生成单页图片，然后移动到笔记输出目录
"""
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Optional, Tuple

from .note_workflow_schemas import NailNotePackage, NailNoteUserInput, NotePageSpec
from .reference_context import ReferenceContext, build_reference_context, reference_context_to_diagnostics


def _get_note_output_dir(package: NailNotePackage) -> Path:
    """获取笔记输出目录（绝对路径）"""
    from project_paths import PROJECT_ROOT, resolve_project_path

    if package.output_dir:
        out = Path(package.output_dir)
        if out.is_absolute():
            return out
        resolved = resolve_project_path(package.output_dir)
        return resolved
    return PROJECT_ROOT / "output" / package.note_id


def _copy_image_to_note_dir(src_path: str, page: NotePageSpec, note_dir: Path) -> str:
    """
    将生成的图片复制到笔记目录，并重命名为 page_XX_role.png。

    Returns:
        相对路径（项目相对路径）
    """
    from project_paths import to_project_relative, resolve_project_path

    src = resolve_project_path(src_path)
    if not src.exists():
        return src_path

    role_name = page.role.value if hasattr(page.role, "value") else str(page.role)
    dest_name = "page_{page_no:02d}_{role_name}.png".format(page_no=page.page_no, role_name=role_name)
    dest = note_dir / dest_name
    shutil.copy2(src, dest)
    return to_project_relative(str(dest))


def _build_page_timing(page: NotePageSpec, duration_sec: float) -> Dict[str, object]:
    role_name = page.role.value if hasattr(page.role, "value") else str(page.role)
    return {
        "page_no": page.page_no,
        "role": role_name,
        "status": page.status,
        "duration_sec": round(duration_sec, 3),
        "used_reference": page.used_reference,
        "image_path": page.image_path,
        "issues": list(page.issues),
    }


def _generate_single_page(
    page: NotePageSpec,
    user_input: NailNoteUserInput,
    note_dir: Path,
    reference_context: Optional[ReferenceContext] = None,
) -> Tuple[NotePageSpec, Dict[str, object]]:
    """
    为单页生成图片并返回页面与 timing diagnostics。
    """
    from orchestrator_v2 import run
    from project_paths import resolve_project_path

    started = time.perf_counter()
    reference_context = reference_context or build_reference_context(user_input, task="poster")

    if not page.prompt:
        page.status = "failed"
        page.issues.append("No prompt available")
        duration_sec = time.perf_counter() - started
        return page, _build_page_timing(page, duration_sec)

    use_reference = reference_context.has_reference
    reference_source_type = reference_context.source_type

    try:
        task = "poster"
        direction = getattr(user_input, "direction", "balanced") or "balanced"
        aspect = getattr(user_input, "aspect", "3:4") or "3:4"
        quality = getattr(user_input, "quality", "final") or "final"

        result = run(
            user_input=page.prompt,
            use_reference=use_reference,
            task=task,
            direction=direction,
            aspect=aspect,
            quality=quality,
            precompiled_brief=True,
            case_id=reference_context.case_id if reference_source_type == "case_id" else None,
            reference_image_path=reference_context.reference_image_path if reference_source_type == "local_path" else None,
            resolved_reference_image_path=reference_context.resolved_image_path if use_reference else None,
            reference_source_type=reference_source_type if use_reference else None,
            dna_summary=reference_context.dna_summary,
            save_case=False,
            archive=True,
            archive_mode="note_only",
            request_id="page_{page_no:02d}".format(page_no=page.page_no),
        )

        if isinstance(result, dict):
            filepath = (
                result.get("filepath")
                or result.get("image_path")
                or result.get("path")
                or result.get("local_path")
            )
            page.image_url = result.get("url")
            page.used_reference = bool(result.get("used_reference", use_reference))
        else:
            filepath = None
            page.used_reference = use_reference

        if filepath:
            resolved = resolve_project_path(filepath)
            if resolved.exists():
                rel_path = _copy_image_to_note_dir(str(resolved), page, note_dir)
                page.image_path = rel_path
                page.status = "generated"
            else:
                page.status = "failed"
                page.issues.append("Resolved filepath does not exist: {path}".format(path=resolved))
        else:
            page.status = "failed"
            page.issues.append("No valid filepath returned: {result}".format(result=result))

    except Exception as exc:
        page.status = "failed"
        page.issues.append(str(exc))

    duration_sec = time.perf_counter() - started
    return page, _build_page_timing(page, duration_sec)


def _apply_failure_flags(package: NailNotePackage) -> None:
    package.partial_failure = False
    for page in package.pages:
        if page.status == "failed":
            package.partial_failure = True
            if page.page_no == 1:
                package.diagnostics["failed_reason"] = "cover_generation_failed"
            break


def generate_note_images(
    package: NailNotePackage,
    user_input: NailNoteUserInput,
    reference_context: Optional[ReferenceContext] = None,
) -> NailNotePackage:
    """
    为笔记的所有页面生成图片。
    支持串行与有限并发，默认串行。
    """
    note_dir = _get_note_output_dir(package)
    note_dir.mkdir(parents=True, exist_ok=True)

    reference_context = reference_context or build_reference_context(user_input, task="poster")
    package.diagnostics["reference"] = reference_context_to_diagnostics(reference_context)

    max_workers = getattr(user_input, "max_workers", 1) or 1
    max_workers = max(1, min(int(max_workers), 3))
    timing_items = []

    if max_workers <= 1:
        for page in package.pages:
            role_name = page.role.value if hasattr(page.role, "value") else page.role
            print("[图片生成] 🖼️ page_{page_no}_{role_name}...".format(page_no=page.page_no, role_name=role_name))
            updated_page, timing_item = _generate_single_page(page, user_input, note_dir, reference_context)
            timing_items.append(timing_item)
            if updated_page.status == "generated":
                print("[图片生成] ✅ page_{page_no}_{role_name} -> {image_path}".format(
                    page_no=updated_page.page_no,
                    role_name=role_name,
                    image_path=updated_page.image_path,
                ))
            else:
                print("[图片生成] ❌ page_{page_no}_{role_name} failed: {issues}".format(
                    page_no=updated_page.page_no,
                    role_name=role_name,
                    issues=", ".join(updated_page.issues),
                ))
    else:
        future_map = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for page in package.pages:
                role_name = page.role.value if hasattr(page.role, "value") else page.role
                print("[图片生成] 🖼️ page_{page_no}_{role_name}...".format(page_no=page.page_no, role_name=role_name))
                future = executor.submit(_generate_single_page, page, user_input, note_dir, reference_context)
                future_map[future] = page

            updated_pages = []
            for future in as_completed(future_map):
                page = future_map[future]
                role_name = page.role.value if hasattr(page.role, "value") else page.role
                try:
                    updated_page, timing_item = future.result()
                except Exception as exc:
                    updated_page = page
                    updated_page.status = "failed"
                    updated_page.issues.append(str(exc))
                    timing_item = _build_page_timing(updated_page, 0.0)
                updated_pages.append(updated_page)
                timing_items.append(timing_item)
                if updated_page.status == "generated":
                    print("[图片生成] ✅ page_{page_no}_{role_name} -> {image_path}".format(
                        page_no=updated_page.page_no,
                        role_name=role_name,
                        image_path=updated_page.image_path,
                    ))
                else:
                    print("[图片生成] ❌ page_{page_no}_{role_name} failed: {issues}".format(
                        page_no=updated_page.page_no,
                        role_name=role_name,
                        issues=", ".join(updated_page.issues),
                    ))
            package.pages = sorted(updated_pages, key=lambda page: page.page_no)

    package.diagnostics["page_timings"] = sorted(timing_items, key=lambda item: item["page_no"])
    _apply_failure_flags(package)
    return package
