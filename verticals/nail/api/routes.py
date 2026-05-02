import json
import re
import shutil
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse, JSONResponse

from project_paths import OUTPUT_DIR, INPUT_DIR, PROJECT_ROOT, resolve_project_path
from verticals.nail.service.job_store import create_job, find_job_by_note_id, get_job
from verticals.nail.service.nail_note_service import create_nail_note
from verticals.nail.service.schemas import NailNoteCreateRequest
from verticals.nail.service.vertical_registry import VerticalRegistry
from verticals.nail.service.history_service import HistoryService
from verticals.nail.service.package_service import PackageService
from verticals.nail.service.case_service import CaseService

from .schemas import HealthResponse, JobCreatedResponse, JobStatusResponse


router = APIRouter()
_NOTE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}

# ── Vertical Registry helpers ────────────────────────────────────────────────

_registry = VerticalRegistry.get_instance()


def _require_vertical(vertical: str) -> None:
    """Raise 400 if vertical is not registered."""
    if not _registry.is_valid_vertical(vertical):
        raise HTTPException(status_code=400, detail=f"unknown vertical: {vertical}")


def _get_history_service() -> HistoryService:
    return HistoryService()


def _get_package_service() -> PackageService:
    return PackageService()


def _get_case_service() -> CaseService:
    return CaseService()


# ── /api/verticals ──────────────────────────────────────────────────────────

class VerticalListResponse(BaseModel if "BaseModel" in dir() else object):
    verticals: List[Dict[str, Any]]


@router.get("/api/verticals")
def list_verticals():
    """Return all registered verticals."""
    verticals = [v.to_dict() for v in _registry.list_verticals()]
    return JSONResponse(content={"verticals": verticals})


# ── /api/verticals/{vertical}/notes ──────────────────────────────────────────

class HistoryListResponse(BaseModel if "BaseModel" in dir() else object):
    items: List[Dict[str, Any]]
    total: int
    vertical: str


@router.get("/api/verticals/{vertical}/notes")
def list_notes(vertical: str, search: Optional[str] = None, has_package: Optional[str] = None, sort: Optional[str] = None):
    """Return服务端历史列表，按 vertical 过滤，支持搜索、过滤、排序。"""
    _require_vertical(vertical)
    svc = _get_history_service()
    items = svc.list_notes(vertical, search=search, has_package=has_package, sort=sort)
    total = len(items)
    return JSONResponse(content={"items": items, "total": total, "vertical": vertical})


# ── /api/verticals/{vertical}/notes/{note_id}/package ───────────────────────

_note_id_re_check = re.compile(r"^[A-Za-z0-9_-]+$")


def _reject_invalid_note_id(note_id: str) -> None:
    if not _note_id_re_check.fullmatch(note_id or ""):
        raise HTTPException(status_code=400, detail="invalid note_id")
    if ".." in note_id or note_id.startswith("/") or "\\" in note_id:
        raise HTTPException(status_code=400, detail="invalid note_id")


@router.get("/api/verticals/{vertical}/notes/{note_id}/package")
def get_note_package(vertical: str, note_id: str):
    """Return note_package.json for the given vertical and note_id."""
    _require_vertical(vertical)
    _reject_invalid_note_id(note_id)

    svc = _get_package_service()
    try:
        package = svc.load_package(vertical, note_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="note package not found")
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return JSONResponse(content=package)


@router.delete("/api/verticals/{vertical}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(vertical: str, note_id: str):
    """Delete a note package directory for the given vertical and note_id."""
    _require_vertical(vertical)
    _reject_invalid_note_id(note_id)

    note_dir = OUTPUT_DIR / note_id
    resolved = note_dir.resolve()
    output_root = OUTPUT_DIR.resolve()
    try:
        resolved.relative_to(output_root)
    except ValueError:
        raise HTTPException(status_code=403, detail="invalid path")

    if not resolved.exists() or not resolved.is_dir():
        raise HTTPException(status_code=404, detail="note not found")

    try:
        shutil.rmtree(resolved)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return None


# ── /api/verticals/{vertical}/cases ─────────────────────────────────────────


@router.get("/api/verticals/{vertical}/cases")
def list_cases(vertical: str):
    _require_vertical(vertical)
    svc = _get_case_service()
    items = svc.list_cases(vertical)
    return JSONResponse(content={"items": items, "total": len(items), "vertical": vertical})


@router.get("/api/verticals/{vertical}/cases/{case_id}")
def get_case(vertical: str, case_id: str):
    _require_vertical(vertical)
    svc = _get_case_service()
    try:
        item = svc.get_case(vertical, case_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"case_id not found or has no image: {case_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return JSONResponse(content=item)


@router.get("/api/verticals/{vertical}/cases/{case_id}/preview-image")
def get_case_preview_image(vertical: str, case_id: str):
    _require_vertical(vertical)
    svc = _get_case_service()
    try:
        image_path = svc.get_case_image_path(vertical, case_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"case_id not found or has no image: {case_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return FileResponse(image_path)


# ── Existing endpoints ────────────────────────────────────────────────────────


def _run_create_job(job_id: str, request: NailNoteCreateRequest) -> None:
    create_nail_note(request, request_id=job_id)


def _derive_job_stage(job: Dict[str, Any]) -> Optional[str]:
    status_value = job.get("status")
    current_stage = job.get("stage")
    if current_stage and not (current_stage == "queued" and status_value != "queued"):
        return current_stage
    if status_value == "queued":
        return "queued"
    if status_value == "running":
        return "workflow_running"
    if status_value in ("succeeded", "partial_failed"):
        return "completed"
    if status_value == "failed":
        return "failed"
    return None


def _compute_elapsed_seconds(job: Dict[str, Any]) -> Optional[float]:
    started_at = job.get("started_at")
    if not started_at:
        return None
    try:
        started = datetime.fromisoformat(started_at)
    except ValueError:
        return None

    end_value = job.get("completed_at") or job.get("finished_at") or job.get("updated_at")
    if not end_value:
        return None
    try:
        end = datetime.fromisoformat(end_value)
    except ValueError:
        return None
    return round(max((end - started).total_seconds(), 0.0), 3)


def _validate_nail_reference_source(request: NailNoteCreateRequest) -> None:
    if request.reference_source != "case_id":
        return

    svc = _get_case_service()
    try:
        svc.get_case("nail", request.case_id or "")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"case_id not found or has no image: {request.case_id}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


def _package_path_for_note(note_id: str) -> Path:
    if not _NOTE_ID_RE.fullmatch(note_id or ""):
        raise ValueError("invalid note_id")
    return resolve_project_path("output/{note_id}/note_package.json".format(note_id=note_id))


def _ensure_output_path(path: Path) -> Path:
    resolved = path.resolve()
    output_root = OUTPUT_DIR.resolve()
    try:
        resolved.relative_to(output_root)
    except ValueError:
        raise ValueError("path escapes output directory")
    return resolved


ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
IMAGE_TYPE_SUFFIXES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/webp": "webp",
}


async def _store_reference_image_upload(file: UploadFile) -> Dict[str, str]:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型 '{file.content_type}'，仅支持 png/jpg/jpeg/webp",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过 10MB 限制，当前 {len(content) // 1024 // 1024}MB",
        )

    suffix = IMAGE_TYPE_SUFFIXES[file.content_type]
    safe_name = f"ref_{uuid.uuid4().hex[:12]}.{suffix}"
    save_dir = INPUT_DIR / "reference_uploads"
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / safe_name

    with open(save_path, "wb") as f:
        f.write(content)

    relative_path = f"input/reference_uploads/{safe_name}"
    preview_url = f"/static/input/reference_uploads/{safe_name}"
    return {"reference_image_path": relative_path, "preview_url": preview_url}


@router.post("/api/verticals/{vertical}/reference-images")
async def upload_vertical_reference_image(vertical: str, file: UploadFile = File(...)):
    _require_vertical(vertical)
    return JSONResponse(await _store_reference_image_upload(file))


@router.post("/api/nail/assets/reference-image")
async def upload_reference_image(file: UploadFile = File(...)):
    """
    Upload a reference image for image-to-image generation.

    Allowed types: png, jpg, jpeg, webp. Max size: 10MB.
    Returns a safe relative path and preview URL (no local absolute paths exposed).
    """
    return JSONResponse(await _store_reference_image_upload(file))


@router.post("/api/nail/notes", response_model=JobCreatedResponse, status_code=status.HTTP_202_ACCEPTED)
def create_note(request: NailNoteCreateRequest) -> JobCreatedResponse:
    import uuid

    _validate_nail_reference_source(request)
    job_id = "job_{token}".format(token=uuid.uuid4().hex[:12])
    payload = request.as_dict()
    create_job(job_id, payload=payload, status="queued")
    worker = threading.Thread(target=_run_create_job, args=(job_id, request), daemon=True, name="nail-note-{job_id}".format(job_id=job_id))
    worker.start()
    return JobCreatedResponse(job_id=job_id, status="queued")


@router.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    job = dict(job)
    job["stage"] = _derive_job_stage(job)
    job["completed_at"] = job.get("completed_at") or job.get("finished_at")
    job["failed_stage"] = job.get("failed_stage")
    job["error_summary"] = job.get("error_summary") or job.get("error")
    job["elapsed_seconds"] = _compute_elapsed_seconds(job)
    return JobStatusResponse(**job)


@router.get("/api/nail/notes/{note_id}/package")
def get_note_package(note_id: str):
    try:
        package_path = _ensure_output_path(_package_path_for_note(note_id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not package_path.exists():
        job = find_job_by_note_id(note_id)
        if job and job.get("package_path"):
            try:
                package_path = _ensure_output_path(resolve_project_path(job["package_path"]))
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc))
    if not package_path.exists():
        raise HTTPException(status_code=404, detail="note package not found")
    data = json.loads(package_path.read_text(encoding="utf-8"))
    return JSONResponse(content=data)
