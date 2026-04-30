from typing import Any, Dict, Optional

try:
    from pydantic import BaseModel, ConfigDict
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseModel
    ConfigDict = dict
    PYDANTIC_V2 = False


class _Model(BaseModel):
    if PYDANTIC_V2:
        model_config = ConfigDict(extra="forbid")


class HealthResponse(_Model):
    status: str


class JobCreatedResponse(_Model):
    job_id: str
    status: str


class JobStatusResponse(_Model):
    job_id: str
    request_id: str
    status: str
    stage: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    note_id: Optional[str] = None
    package_path: Optional[str] = None
    output_dir: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    completed_at: Optional[str] = None
    elapsed_seconds: Optional[float] = None
    error: Optional[str] = None
    failed_stage: Optional[str] = None
    error_summary: Optional[str] = None
    payload: Dict[str, Any] = {}
    diagnostics: Optional[Dict[str, Any]] = None
