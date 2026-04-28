"""
asset_manager.py — Asset archival for history record system.
Handles copying/archiving reference images, generated images, and thumbnails
to record_dir/assets/* with project-relative paths, sha256, dimensions.
"""

from pathlib import Path
import shutil
import hashlib
import struct
from datetime import datetime
from typing import Optional

from project_paths import PROJECT_ROOT, to_project_relative, resolve_project_path


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def get_image_dimensions(filepath: Path) -> tuple[int, int]:
    """Return (width, height) by reading image headers. PNG/JPEG/WebP supported."""
    try:
        data = filepath.read_bytes()
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            w = struct.unpack(">I", data[16:20])[0]
            h = struct.unpack(">I", data[20:24])[0]
            return w, h
        # JPEG — use EXIF or SOF0; fallback to 0,0 for simplicity
        if data[:2] == b"\xff\xd8":
            return 0, 0
        # WebP
        if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            return 0, 0
        return 0, 0
    except Exception:
        return 0, 0


def archive_reference_image(
    source_path: str,
    record_dir: Path,
    reference_id: str = "ref_001",
    source_type: str = "local_path",
    source_value: str = None,
    source_task: str = None,
    influence_scope: list = None,
) -> dict:
    """
    Copy a reference image into record_dir/assets/references/.
    Returns a ReferenceAsset dict with all metadata fields.

    Args:
        source_path: original path to the reference image (used to copy)
        record_dir: the record directory to archive into
        reference_id: e.g. "ref_001"
        source_type: one of "case_id", "local_path", "upload", "history_record"
        source_value: for case_id this is the case_id string; for local_path it's the project-relative path
        source_task: the task type (poster/product/ppt/etc.) if from case library
        influence_scope: list of page IDs influenced, e.g. ["page_01"] or ["global"]
    """
    if influence_scope is None:
        influence_scope = ["global"]

    # Resolve actual file path
    src = resolve_project_path(source_path)
    original_path_rel = to_project_relative(src)  # always project-relative

    if not src.exists():
        return _make_reference_asset(
            reference_id=reference_id,
            original_path=original_path_rel,
            archived_path=None,
            thumbnail_path=None,
            filename=None,
            exists=False,
            source_type="local_path",
            source_value=source_value or original_path_rel,
            source_task=source_task,
            influence_scope=influence_scope,
        )

    refs_dir = record_dir / "assets" / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)

    ext = src.suffix or ".png"
    filename = f"{reference_id}{ext}"
    archived_path = refs_dir / filename

    shutil.copy2(src, archived_path)

    size = src.stat().st_size
    sha = compute_sha256(archived_path)
    w, h = get_image_dimensions(archived_path)

    return _make_reference_asset(
        reference_id=reference_id,
        original_path=original_path_rel,
        archived_path=to_project_relative(archived_path),
        thumbnail_path=None,  # thumbnail generation deferred
        filename=filename,
        content_type=f"image/{ext.lstrip('.')}",
        file_size=size,
        width=w,
        height=h,
        sha256=sha,
        exists=True,
        source_type=source_type,
        source_value=source_value or original_path_rel,
        source_task=source_task,
        influence_scope=influence_scope,
    )


def archive_generated_image(
    source_path: str,
    record_dir: Path,
    page_id: str,
    role: str,
) -> dict:
    """
    Copy a generated image into record_dir/assets/generated/.
    Returns a GeneratedAsset dict.
    """
    src = resolve_project_path(source_path)
    gen_dir = record_dir / "assets" / "generated"
    gen_dir.mkdir(parents=True, exist_ok=True)

    ext = src.suffix or ".png"
    filename = f"{page_id}_{role}{ext}"
    archived_path = gen_dir / filename

    if src.exists():
        shutil.copy2(src, archived_path)

    size = src.stat().st_size if src.exists() else 0
    sha = compute_sha256(archived_path) if src.exists() else ""
    w, h = get_image_dimensions(archived_path) if src.exists() else (0, 0)

    return {
        "asset_id": page_id,
        "filename": filename,
        "archived_path": to_project_relative(archived_path) if src.exists() else None,
        "content_type": f"image/{ext.lstrip('.')}",
        "file_size": size,
        "width": w,
        "height": h,
        "sha256": sha,
        "exists": src.exists(),
    }


def _make_reference_asset(
    reference_id: str,
    original_path: str,
    archived_path: Optional[str],
    thumbnail_path: Optional[str],
    filename: Optional[str],
    exists: bool,
    source_type: str = "local_path",
    source_value: str = None,
    source_task: Optional[str] = None,
    influence_scope: list = None,
    content_type: str = "image/png",
    file_size: int = 0,
    width: int = 0,
    height: int = 0,
    sha256: str = "",
) -> dict:
    if influence_scope is None:
        influence_scope = ["style"] if exists else []
    return {
        "reference_id": reference_id,
        "enabled": exists,
        "source_type": source_type,
        "source_value": source_value or original_path,
        "source_task": source_task,
        "source_record_id": None,
        "original_path": original_path,
        "archived_path": archived_path,
        "thumbnail_path": thumbnail_path,
        "filename": filename,
        "content_type": content_type,
        "file_size": file_size,
        "width": width,
        "height": height,
        "sha256": sha256,
        "exists": exists,
        "usage_policy": "copy" if exists else "unavailable",
        "influence_scope": influence_scope if exists else [],
        "dna": None,
    }