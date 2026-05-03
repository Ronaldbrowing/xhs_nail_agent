"""
Case Service — reads vertical-scoped case library entries for APIs.

Handles:
- Vertical -> case task mapping
- Listing cases under the mapped task directory
- Resolving a single case by case_id within the requested vertical scope
- Safe relative image paths for API responses
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from project_paths import CASE_LIBRARY_DIR, PROJECT_ROOT


class CaseService:
    """Read-only access layer for case library APIs."""

    _CASE_ID_RE = re.compile(r"^case_[A-Za-z0-9_-]+$")
    _IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")
    _VERTICAL_TASK_MAP = {
        "nail": "poster",
    }

    def __init__(self, case_root: Optional[Path] = None):
        self.case_root = case_root or CASE_LIBRARY_DIR

    def _task_for_vertical(self, vertical: str) -> str:
        task = self._VERTICAL_TASK_MAP.get(vertical)
        if not task:
            raise ValueError(f"unsupported vertical: {vertical}")
        return task

    def _validate_case_id(self, case_id: str) -> None:
        if not case_id or not self._CASE_ID_RE.fullmatch(case_id):
            raise ValueError(f"invalid case_id: {case_id}")

    def _task_dir(self, vertical: str) -> Path:
        task = self._task_for_vertical(vertical)
        return self.case_root / task

    def _find_case_dir(self, vertical: str, case_id: str) -> Path:
        self._validate_case_id(case_id)
        task_dir = self._task_dir(vertical)
        if not task_dir.exists():
            raise FileNotFoundError(f"case_id not found: {case_id}")

        for entry in sorted(task_dir.iterdir()):
            if entry.is_dir() and entry.name.startswith(case_id):
                return entry
        raise FileNotFoundError(f"case_id not found: {case_id}")

    def _find_image(self, case_dir: Path) -> Optional[Path]:
        for suffix in self._IMAGE_SUFFIXES:
            candidate = case_dir / f"image{suffix}"
            if candidate.exists():
                return candidate
        return None

    def _safe_relative(self, path: Path) -> str:
        resolved = path.resolve()
        try:
            return str(resolved.relative_to(PROJECT_ROOT))
        except ValueError:
            try:
                return str(resolved.relative_to(self.case_root.parent.resolve()))
            except ValueError:
                return resolved.name

    def _load_case(self, vertical: str, case_dir: Path) -> Dict[str, Any]:
        meta_file = case_dir / "metadata.json"
        if not meta_file.exists():
            raise FileNotFoundError(f"metadata missing for case: {case_dir.name}")

        try:
            metadata = json.loads(meta_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"corrupted case metadata for {case_dir.name}: {exc}")

        image_path = self._find_image(case_dir)
        relative_image_path = self._safe_relative(image_path) if image_path else None
        stored_case_id = metadata.get("case_id")
        fallback_case_id = case_dir.name.split("_", 2)
        if stored_case_id:
            case_id = stored_case_id
        elif len(fallback_case_id) >= 2 and fallback_case_id[0] == "case":
            case_id = "_".join(fallback_case_id[:2])
        else:
            case_id = case_dir.name

        return {
            "case_id": case_id,
            "vertical": vertical,
            "task": self._task_for_vertical(vertical),
            "title": metadata.get("brief") or case_dir.name,
            "brief": metadata.get("brief", ""),
            "tags": metadata.get("tags", []),
            "rating": metadata.get("rating", 0),
            "created_at": metadata.get("created_at"),
            "image_path": relative_image_path,
            "has_image": bool(image_path),
            "preview_url": self.build_preview_url(vertical, case_id) if image_path else None,
        }

    def build_preview_url(self, vertical: str, case_id: str) -> str:
        self._task_for_vertical(vertical)
        self._validate_case_id(case_id)
        return f"/api/verticals/{vertical}/cases/{case_id}/preview-image"

    def get_case_image_path(self, vertical: str, case_id: str) -> Path:
        case_dir = self._find_case_dir(vertical, case_id)
        image_path = self._find_image(case_dir)
        if not image_path or not image_path.exists():
            raise FileNotFoundError(f"case_id not found or has no image: {case_id}")
        return image_path.resolve()

    def list_cases(self, vertical: str) -> List[Dict[str, Any]]:
        task_dir = self._task_dir(vertical)
        if not task_dir.exists():
            return []

        items: List[Dict[str, Any]] = []
        for entry in sorted(task_dir.iterdir()):
            if not entry.is_dir() or not entry.name.startswith("case_"):
                continue
            try:
                items.append(self._load_case(vertical, entry))
            except (FileNotFoundError, ValueError):
                continue

        items.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return items

    def get_case(self, vertical: str, case_id: str) -> Dict[str, Any]:
        case_dir = self._find_case_dir(vertical, case_id)
        case = self._load_case(vertical, case_dir)
        if case.get("case_id") != case_id:
            case["case_id"] = case_id
        return case
