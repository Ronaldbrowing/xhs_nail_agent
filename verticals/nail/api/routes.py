import json
import threading
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from project_paths import OUTPUT_DIR, resolve_project_path
from verticals.nail.service.job_store import create_job, find_job_by_note_id, get_job
from verticals.nail.service.nail_note_service import create_nail_note
from verticals.nail.service.schemas import NailNoteCreateRequest

from .schemas import HealthResponse, JobCreatedResponse, JobStatusResponse


router = APIRouter()


def _run_create_job(job_id: str, request: NailNoteCreateRequest) -> None:
    create_nail_note(request, request_id=job_id)


def _package_path_for_note(note_id: str) -> Path:
    return resolve_project_path("output/{note_id}/note_package.json".format(note_id=note_id))


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


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
    package_path = _package_path_for_note(note_id)
    if not package_path.exists():
        job = find_job_by_note_id(note_id)
        if job and job.get("package_path"):
            package_path = resolve_project_path(job["package_path"])
    if not package_path.exists():
        raise HTTPException(status_code=404, detail="note package not found")
    data = json.loads(package_path.read_text(encoding="utf-8"))
    return JSONResponse(content=data)
