import json
import shutil
import time
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from project_paths import PROJECT_ROOT, resolve_project_path
from verticals.nail.service import job_store


class NailFastAPITests(unittest.TestCase):
    def setUp(self):
        from verticals.nail.api.app import app

        self.client = TestClient(app)
        job_store.reset_jobs()
        self._cleanup_dirs = []

    def tearDown(self):
        job_store.reset_jobs()
        for path in self._cleanup_dirs:
            shutil.rmtree(path, ignore_errors=True)

    def _wait_for_job(self, job_id, timeout_sec=10.0):
        deadline = time.time() + timeout_sec
        last_payload = None
        while time.time() < deadline:
            response = self.client.get("/api/jobs/{job_id}".format(job_id=job_id))
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            last_payload = payload
            if payload["status"] in ("succeeded", "failed", "partial_failed"):
                return payload
            time.sleep(0.1)
        self.fail("job did not finish in time: {payload}".format(payload=last_payload))

    def test_health_returns_ok(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_post_generate_images_false_returns_job_and_package(self):
        response = self.client.post(
            "/api/nail/notes",
            json={
                "brief": "夏日蓝色猫眼短甲",
                "generate_images": False,
                "generate_copy": True,
                "generate_tags": True,
                "max_workers": 1,
            },
        )
        self.assertEqual(response.status_code, 202)
        payload = response.json()
        self.assertIn("job_id", payload)
        self.assertEqual(payload["status"], "queued")

        job_payload = self._wait_for_job(payload["job_id"])
        self.assertEqual(job_payload["status"], "succeeded")
        package_path = job_payload["package_path"]
        self.assertTrue(package_path)
        self.assertTrue(resolve_project_path(package_path).exists())
        note_id = job_payload["note_id"]
        self.assertTrue(note_id)
        self._cleanup_dirs.append(resolve_project_path("output/{note_id}".format(note_id=note_id)))

        package_response = self.client.get("/api/nail/notes/{note_id}/package".format(note_id=note_id))
        self.assertEqual(package_response.status_code, 200)
        package_data = package_response.json()
        self.assertEqual(package_data["note_id"], note_id)
        self.assertEqual(package_data["package_path"], package_path)
