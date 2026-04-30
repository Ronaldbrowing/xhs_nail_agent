import json
import re
import shutil
import threading
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse

from project_paths import OUTPUT_DIR, INPUT_DIR, PROJECT_ROOT, resolve_project_path
from verticals.nail.service.job_store import create_job, find_job_by_note_id, get_job
from verticals.nail.service.nail_note_service import create_nail_note
from verticals.nail.service.schemas import NailNoteCreateRequest

from .schemas import HealthResponse, JobCreatedResponse, JobStatusResponse


router = APIRouter()
_NOTE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def _run_create_job(job_id: str, request: NailNoteCreateRequest) -> None:
    create_nail_note(request, request_id=job_id)


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


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
IMAGE_TYPE_SUFFIXES = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/webp": "webp",
}


@router.post("/api/nail/assets/reference-image")
async def upload_reference_image(file: UploadFile = File(...)):
    """
    Upload a reference image for image-to-image generation.

    Allowed types: png, jpg, jpeg, webp. Max size: 10MB.
    Returns a safe relative path and preview URL (no local absolute paths exposed).
    """
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

    # Return relative path (safe for frontend) and preview URL
    relative_path = f"input/reference_uploads/{safe_name}"
    preview_url = f"/static/input/reference_uploads/{safe_name}"
    return JSONResponse({"reference_image_path": relative_path, "preview_url": preview_url})


@router.post("/api/nail/notes", response_model=JobCreatedResponse, status_code=status.HTTP_202_ACCEPTED)
def create_note(request: NailNoteCreateRequest) -> JobCreatedResponse:
    import uuid

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
