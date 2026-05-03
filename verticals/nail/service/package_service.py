"""
Package Service — loads and validates note_package.json for replay.

Handles:
- Path security (note_id whitelist, directory containment)
- Vertical-aware lookup (only find within requested vertical scope)
- Vertical mismatch detection
- Missing field normalization
- Corrupted JSON handling
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class PackageService:
    """
    Loads and validates note_package.json with path safety and vertical awareness.

    Supports configurable output_root for testing.
    """

    _NOTE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")

    def __init__(self, output_root: Optional[Path] = None):
        """
        Initialize PackageService.

        Args:
            output_root: Path to output directory. Defaults to project output/.
                         Allows injection for testing.
        """
        from project_paths import OUTPUT_DIR

        self.output_root = output_root or OUTPUT_DIR

    def _validate_note_id(self, note_id: str) -> None:
        """Raise ValueError if note_id is invalid or suspicious."""
        if not note_id or not self._NOTE_ID_RE.fullmatch(note_id):
            raise ValueError(f"invalid note_id: {note_id}")

    def _safe_resolve(self, note_id: str) -> Path:
        """
        Resolve note_id to a safe path within output_root.

        Raises ValueError if path escapes output_root.
        """
        self._validate_note_id(note_id)
        candidate = self.output_root / note_id / "note_package.json"
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self.output_root.resolve())
        except ValueError:
            raise ValueError(f"note_id '{note_id}' resolves outside output directory")
        return resolved

    def find_package(
        self, vertical: str, note_id: str
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Load a note_package.json for the given vertical and note_id.

        Args:
            vertical: The vertical to scope the search.
            note_id: The note ID.

        Returns:
            Tuple of (package_data, field_sources dict).

        Raises:
            FileNotFoundError: note_id not found.
            ValueError: path traversal attempt or invalid note_id.
            PermissionError: vertical mismatch (package vertical != request vertical).
        """
        try:
            package_path = self._safe_resolve(note_id)
        except ValueError:
            raise ValueError(f"invalid note_id: {note_id}")

        if not package_path.exists():
            raise FileNotFoundError(f"note_id '{note_id}' not found")

        try:
            data = json.loads(package_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"corrupted package JSON for note_id '{note_id}': {e}")

        package_vertical = data.get("vertical")
        field_sources = {}

        if package_vertical:
            field_sources["vertical"] = "explicit"
            if package_vertical != vertical:
                raise PermissionError(
                    f"vertical mismatch: package belongs to '{package_vertical}', "
                    f"requested vertical is '{vertical}'"
                )
        else:
            if note_id.startswith(f"{vertical}_"):
                field_sources["vertical"] = "inferred"
            else:
                raise PermissionError(
                    f"vertical mismatch: package has no explicit vertical, "
                    f"and note_id '{note_id}' does not match requested vertical '{vertical}'"
                )

        content_platform = data.get("content_platform")
        if content_platform:
            field_sources["content_platform"] = "explicit"
        else:
            content_platform = "xhs"
            field_sources["content_platform"] = "inferred"

        content_type = data.get("content_type")
        if content_type:
            field_sources["content_type"] = "explicit"
        else:
            content_type = "image_text_note"
            field_sources["content_type"] = "inferred"

        return data, field_sources

    def load_package(self, vertical: str, note_id: str) -> Dict[str, Any]:
        """
        Public API: load and return package data with field_sources.

        Returns normalized package dict.
        Raises ValueError for path/security issues.
        Raises FileNotFoundError for missing packages.
        """
        data, field_sources = self.find_package(vertical, note_id)
        data["_field_sources"] = field_sources
        if not data.get("vertical"):
            data["vertical"] = vertical
        if not data.get("content_platform"):
            data["content_platform"] = "xhs"
        if not data.get("content_type"):
            data["content_type"] = "image_text_note"
        return data