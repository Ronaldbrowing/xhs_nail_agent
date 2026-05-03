"""
History Service — scans output directory for historical note packages.

Handles:
- Directory scanning for note_package.json files
- Missing field fallback (explicit / inferred / unknown)
- Corrupted package skipping
- Vertical filtering
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class HistoryService:
    """
    Scans output directory for historical note packages.

    Supports configurable output_root for testing.
    """

    _NOTE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")

    def __init__(self, output_root: Optional[Path] = None):
        """
        Initialize HistoryService.

        Args:
            output_root: Path to output directory. Defaults to project output/.
                         Allows injection for testing.
        """
        from project_paths import OUTPUT_DIR

        self.output_root = output_root or OUTPUT_DIR

    def list_notes(
        self,
        vertical: str,
        search: Optional[str] = None,
        has_package: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all note packages for a given vertical with optional search, filter, and sort.

        Args:
            vertical: The vertical to filter by.
            search: Optional string to fuzzy-match against note_id and selected_title.
            has_package: Optional filter — "true" (has package), "false" (no package), "all" (no filter).
            sort: Optional sort order — "created_at_desc" (newest first) or "created_at_asc" (oldest first).
                  Defaults to "created_at_desc".

        Returns:
            List of note history items with field_sources标记.
        """
        items = []
        if not self.output_root.exists():
            return items

        for entry in self.output_root.iterdir():
            if not entry.is_dir():
                continue
            note_id = entry.name
            if not self._NOTE_ID_RE.fullmatch(note_id):
                continue
            package_path = entry / "note_package.json"
            if not package_path.exists():
                continue
            try:
                data = json.loads(package_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            item_vertical = data.get("vertical")
            field_sources = {}

            if item_vertical:
                field_sources["vertical"] = "explicit"
                if item_vertical != vertical:
                    continue
            else:
                if note_id.startswith(f"{vertical}_"):
                    item_vertical = vertical
                    field_sources["vertical"] = "inferred"
                else:
                    continue

            content_platform = data.get("content_platform")
            if content_platform:
                source_platform = "explicit"
            else:
                content_platform = "xhs"
                source_platform = "inferred"

            content_type = data.get("content_type")
            if content_type:
                source_type = "explicit"
            else:
                content_type = "image_text_note"
                source_type = "inferred"

            status = data.get("status", "unknown")
            pages = data.get("pages", [])
            has_pkg = len(pages) > 0 if pages else False

            selected_title = data.get("selected_title") or data.get("title")

            # --- Search filter ---
            if search and search.strip():
                term = search.strip().lower()
                title_text = (selected_title or "").lower()
                id_text = note_id.lower()
                if term not in title_text and term not in id_text:
                    continue

            # --- has_package filter ---
            if has_package and has_package != "all":
                if has_package == "true" and not has_pkg:
                    continue
                if has_package == "false" and has_pkg:
                    continue

            items.append(
                {
                    "note_id": note_id,
                    "vertical": item_vertical or vertical,
                    "content_platform": content_platform,
                    "content_type": content_type,
                    "scenario": data.get("scenario"),
                    "brief": data.get("brief"),
                    "selected_title": selected_title,
                    "status": status,
                    "created_at": data.get("created_at"),
                    "has_package": has_pkg,
                    "field_sources": {
                        "vertical": field_sources["vertical"],
                        "content_platform": source_platform,
                        "content_type": source_type,
                    },
                }
            )

        # --- Sort ---
        sort_key = (sort == "created_at_asc")
        items.sort(key=lambda x: x.get("created_at") or "", reverse=not sort_key)
        return items

    def get_total(self, vertical: str) -> int:
        """Return total count of notes for vertical."""
        return len(self.list_notes(vertical))