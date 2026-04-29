import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from project_paths import OUTPUT_DIR


_JOBS: Dict[str, Dict[str, Any]] = {}
_JOB_STORE_PATH = OUTPUT_DIR / "nail_jobs.json"


def _persist() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(_JOB_STORE_PATH, "w", encoding="utf-8") as handle:
        json.dump(_JOBS, handle, ensure_ascii=False, indent=2)


def create_job(job_id: str, payload: Optional[Dict[str, Any]] = None, status: str = "queued") -> Dict[str, Any]:
    record = {
        "job_id": job_id,
        "status": status,
        "payload": payload or {},
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    _JOBS[job_id] = record
    _persist()
    return record


def update_job(job_id: str, **fields) -> Dict[str, Any]:
    record = _JOBS.get(job_id)
    if record is None:
        record = create_job(job_id)
    record.update(fields)
    record["updated_at"] = datetime.now().isoformat()
    _persist()
    return record


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    return _JOBS.get(job_id)


def list_jobs() -> List[Dict[str, Any]]:
    return list(_JOBS.values())
