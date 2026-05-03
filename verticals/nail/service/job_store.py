import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from project_paths import OUTPUT_DIR


_JOBS: Dict[str, Dict[str, Any]] = {}
_JOB_STORE_PATH = OUTPUT_DIR / "nail_jobs.json"
_LOCK = threading.RLock()


def _load() -> None:
    """Restore _JOBS from persistent storage on module init."""
    if _JOB_STORE_PATH.exists():
        with open(_JOB_STORE_PATH, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            if isinstance(loaded, dict):
                _JOBS.update(loaded)


def _persist() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(_JOB_STORE_PATH, "w", encoding="utf-8") as handle:
        json.dump(_JOBS, handle, ensure_ascii=False, indent=2)


def create_job(job_id: str, payload: Optional[Dict[str, Any]] = None, status: str = "queued") -> Dict[str, Any]:
    with _LOCK:
        record = {
            "job_id": job_id,
            "request_id": job_id,
            "status": status,
            "stage": "queued",
            "payload": payload or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "started_at": None,
            "finished_at": None,
            "completed_at": None,
            "note_id": None,
            "package_path": None,
            "output_dir": None,
            "error": None,
            "failed_stage": None,
            "error_summary": None,
        }
        _JOBS[job_id] = record
        _persist()
        return dict(record)


def update_job(job_id: str, **fields) -> Dict[str, Any]:
    with _LOCK:
        record = _JOBS.get(job_id)
        if record is None:
            record = create_job(job_id)

        if "finished_at" in fields and "completed_at" not in fields:
            fields["completed_at"] = fields["finished_at"]
        if "completed_at" in fields and "finished_at" not in fields:
            fields["finished_at"] = fields["completed_at"]

        record.update(fields)
        record["updated_at"] = fields.get("updated_at", datetime.now().isoformat())
        _persist()
        return dict(record)


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    with _LOCK:
        record = _JOBS.get(job_id)
        return dict(record) if record is not None else None


def list_jobs() -> List[Dict[str, Any]]:
    with _LOCK:
        return [dict(item) for item in _JOBS.values()]


def find_job_by_note_id(note_id: str) -> Optional[Dict[str, Any]]:
    with _LOCK:
        for item in _JOBS.values():
            if item.get("note_id") == note_id:
                return dict(item)
    return None


def reset_jobs() -> None:
    with _LOCK:
        _JOBS.clear()
        if _JOB_STORE_PATH.exists():
            _JOB_STORE_PATH.unlink()


# Restore _JOBS from persistent storage on module import
_load()
