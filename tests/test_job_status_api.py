from fastapi.testclient import TestClient

from verticals.nail.api.app import app
from verticals.nail.service import job_store


def setup_function():
    job_store.reset_jobs()


def teardown_function():
    job_store.reset_jobs()


def test_job_status_returns_enriched_metadata_for_terminal_success():
    client = TestClient(app)
    job_store.create_job("job_done", payload={"brief": "done"})
    job_store.update_job(
        "job_done",
        status="succeeded",
        stage="completed",
        started_at="2026-04-30T18:00:00",
        completed_at="2026-04-30T18:00:01.250000",
        updated_at="2026-04-30T18:00:01.250000",
        note_id="nail_demo",
        package_path="output/nail_demo/note_package.json",
        output_dir="output/nail_demo",
    )

    response = client.get("/api/jobs/job_done")
    assert response.status_code == 200
    payload = response.json()

    assert payload["job_id"] == "job_done"
    assert payload["status"] == "succeeded"
    assert payload["stage"] == "completed"
    assert payload["started_at"] == "2026-04-30T18:00:00"
    assert payload["completed_at"] == "2026-04-30T18:00:01.250000"
    assert payload["finished_at"] == "2026-04-30T18:00:01.250000"
    assert payload["elapsed_seconds"] == 1.25
    assert payload["failed_stage"] is None
    assert payload["error_summary"] is None


def test_job_status_returns_failed_stage_and_error_summary_for_failed_job():
    client = TestClient(app)
    job_store.create_job("job_failed", payload={"brief": "failed"})
    job_store.update_job(
        "job_failed",
        status="failed",
        stage="failed",
        started_at="2026-04-30T18:05:00",
        finished_at="2026-04-30T18:05:02",
        failed_stage="workflow",
        error="boom",
        error_summary="boom",
    )

    response = client.get("/api/jobs/job_failed")
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "failed"
    assert payload["stage"] == "failed"
    assert payload["completed_at"] == "2026-04-30T18:05:02"
    assert payload["finished_at"] == "2026-04-30T18:05:02"
    assert payload["elapsed_seconds"] == 2.0
    assert payload["failed_stage"] == "workflow"
    assert payload["error_summary"] == "boom"
    assert payload["error"] == "boom"


def test_job_status_derives_stage_and_elapsed_for_legacy_record():
    client = TestClient(app)
    created = job_store.create_job("job_legacy", payload={"brief": "legacy"})
    job_store.update_job(
        "job_legacy",
        status="running",
        started_at="2026-04-30T18:10:00",
        updated_at="2026-04-30T18:10:03",
    )

    response = client.get("/api/jobs/job_legacy")
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "running"
    assert payload["stage"] == "workflow_running"
    assert payload["completed_at"] is None
    assert payload["elapsed_seconds"] == 3.0
    assert payload["request_id"] == created["request_id"]
