#!/usr/bin/env python3
import json
import time
import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from verticals.nail.api.app import app
from verticals.nail.service import job_store


def wait_for_job(client, job_id, timeout_sec=10.0):
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        response = client.get("/api/jobs/{job_id}".format(job_id=job_id))
        payload = response.json()
        if payload["status"] in ("succeeded", "failed", "partial_failed"):
            return payload
        time.sleep(0.1)
    raise RuntimeError("job did not finish in time")


def main():
    job_store.reset_jobs()
    client = TestClient(app)

    health = client.get("/health")
    print("health:", health.status_code, health.json())

    created = client.post(
        "/api/nail/notes",
        json={
            "brief": "夏日蓝色猫眼短甲",
            "generate_images": False,
            "generate_copy": True,
            "generate_tags": True,
            "max_workers": 1,
        },
    )
    print("create:", created.status_code, created.json())

    job_payload = wait_for_job(client, created.json()["job_id"])
    print("job:", json.dumps(job_payload, ensure_ascii=False, indent=2))

    package = client.get("/api/nail/notes/{note_id}/package".format(note_id=job_payload["note_id"]))
    print("package:", package.status_code, package.json()["note_id"], package.json()["package_path"])


if __name__ == "__main__":
    main()
