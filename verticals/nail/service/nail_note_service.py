import uuid
from datetime import datetime
from typing import List, Optional

from verticals.nail.note_workflow import NailNoteWorkflow
from verticals.nail.note_workflow_schemas import NailNotePackage

from .job_store import create_job, update_job
from .schemas import NailNoteCreateRequest, NailNoteCreateResponse, NailNotePageResponse


def _package_status(package: NailNotePackage) -> str:
    if package.success and package.partial_failure:
        return "partial_failed"
    if package.success:
        return "succeeded"
    if package.partial_failure:
        return "partial_failed"
    return "failed"


def build_create_response(
    request_id: str,
    package: Optional[NailNotePackage],
    status: str,
    errors: Optional[List[str]] = None,
) -> NailNoteCreateResponse:
    page_items = []
    diagnostics = {}
    if package is not None:
        for page in getattr(package, "pages", []) or []:
            role = page.role.value if hasattr(page.role, "value") else str(page.role)
            page_items.append(
                NailNotePageResponse(
                    page_no=page.page_no,
                    role=role,
                    status=page.status,
                    image_path=page.image_path,
                    used_reference=page.used_reference,
                    issues=list(page.issues),
                )
            )
        diagnostics = dict(getattr(package, "diagnostics", {}) or {})

    return NailNoteCreateResponse(
        request_id=request_id,
        note_id=getattr(package, "note_id", None) if package is not None else None,
        status=status,
        package_path=getattr(package, "package_path", None) if package is not None else None,
        output_dir=getattr(package, "output_dir", None) if package is not None else None,
        success=bool(getattr(package, "success", False)) if package is not None else False,
        partial_failure=bool(getattr(package, "partial_failure", False)) if package is not None else False,
        qa_score=diagnostics.get("qa_score"),
        pages=page_items,
        diagnostics=diagnostics,
        errors=errors or [],
    )


def create_nail_note(request: NailNoteCreateRequest, request_id: Optional[str] = None) -> NailNoteCreateResponse:
    request_id = request_id or "req_{token}".format(token=uuid.uuid4().hex[:12])
    payload = request.as_dict()
    if create_job is not None:
        existing = None
        try:
            from .job_store import get_job
            existing = get_job(request_id)
        except Exception:
            existing = None
        if existing is None:
            create_job(request_id, payload=payload, status="queued")
    update_job(request_id, status="running", started_at=datetime.now().isoformat(), error=None)

    workflow = NailNoteWorkflow()
    try:
        package = workflow.generate_note(request.to_user_input(request_id=request_id))
        status = _package_status(package)
        update_job(
            request_id,
            status=status,
            note_id=package.note_id,
            package_path=package.package_path,
            output_dir=package.output_dir,
            finished_at=datetime.now().isoformat(),
        )
        return build_create_response(request_id=request_id, package=package, status=status, errors=[])
    except Exception as exc:
        update_job(request_id, status="failed", error=str(exc), finished_at=datetime.now().isoformat())
        return build_create_response(
            request_id=request_id,
            package=None,
            status="failed",
            errors=[str(exc)],
        )
