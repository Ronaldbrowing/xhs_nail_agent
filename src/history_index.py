"""
history_index.py — Append-only history index for frontend list loading.
Writes one JSON line per record to output/records/history_index.jsonl.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from project_paths import OUTPUT_DIR, to_project_relative


def ensure_history_index() -> Path:
    """Ensure records dir and history_index.jsonl exist."""
    records_dir = OUTPUT_DIR / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    index_path = records_dir / "history_index.jsonl"
    if not index_path.exists():
        index_path.touch()
    return index_path


def append_history_index(
    record_id: str,
    record_type: str,
    created_at: str,
    updated_at: str,
    status: str,
    title: str,
    brief: str,
    style_id: Optional[str],
    style_label: Optional[str],
    note_goal: Optional[str],
    page_count: int,
    cover_image_path: Optional[str],
    reference_thumbnail_path: Optional[str],
    used_reference: bool,
    overall_score: float,
    package_path: str,
    search_text: str,
) -> None:
    """
    Append one HistoryIndexItem as a JSON line to history_index.jsonl.
    """
    index_path = ensure_history_index()

    item = {
        "record_id": record_id,
        "record_type": record_type,
        "schema_version": "1.0",
        "created_at": created_at,
        "updated_at": updated_at,
        "status": status,
        "title": title,
        "brief": brief,
        "style_id": style_id,
        "style_label": style_label,
        "note_goal": note_goal,
        "page_count": page_count,
        "cover_image_path": cover_image_path,
        "reference_thumbnail_path": reference_thumbnail_path,
        "used_reference": used_reference,
        "overall_score": overall_score,
        "package_path": package_path,
        "search_text": search_text,
    }

    with open(index_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def build_search_text(brief: str, style_id: Optional[str], tags: list) -> str:
    """Build combined search text for frontend filtering."""
    parts = [brief or ""]
    if style_id:
        parts.append(style_id)
    parts.extend(tags or [])
    return " ".join(parts).strip()