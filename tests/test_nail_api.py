import json
import shutil
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

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

    def test_root_serves_html_with_web_asset_references(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        body = response.text
        self.assertIn("Vertical Content Studio", body)
        self.assertIn("AI 内容生成工作台", body)
        self.assertIn("输入需求", body)
        self.assertIn("内容需求", body)
        self.assertIn("使用示例", body)
        self.assertIn("当前内容场景", body)
        self.assertIn("继续查询", body)
        self.assertIn("发现上次任务", body)
        self.assertIn("/web/style.css", body)
        self.assertIn("/web/app.js", body)

    def test_web_assets_are_accessible(self):
        js_response = self.client.get("/web/app.js")
        self.assertEqual(js_response.status_code, 200)
        self.assertIn("javascript", js_response.headers.get("content-type", ""))
        js_body = js_response.text
        self.assertIn('resumePanel.removeAttribute("hidden")', js_body)
        self.assertIn('resumePanel.style.display = ""', js_body)
        self.assertIn('console.error("resume-panel element is missing"', js_body)
        self.assertIn("renderPartialFailedJob", js_body)
        self.assertIn("部分完成，但结果包读取失败", js_body)

        css_response = self.client.get("/web/style.css")
        self.assertEqual(css_response.status_code, 200)
        self.assertIn("text/css", css_response.headers.get("content-type", ""))
        css_body = css_response.text
        self.assertIn(".resume-panel-inline", css_body)
        self.assertIn("background: #fff8f6;", css_body)

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

    def test_post_same_second_jobs_produce_unique_note_ids_and_output_dirs(self):
        fixed_now = datetime(2026, 4, 29, 17, 21, 24)

        class FixedDateTime(object):
            @classmethod
            def now(cls):
                return fixed_now

        payload = {
            "brief": "夏日蓝色猫眼短甲",
            "style_id": "default",
            "generate_images": False,
            "generate_copy": True,
            "generate_tags": True,
        }

        with patch("verticals.nail.note_workflow.datetime", FixedDateTime):
            first = self.client.post("/api/nail/notes", json=payload)
            second = self.client.post("/api/nail/notes", json=payload)
            self.assertEqual(first.status_code, 202)
            self.assertEqual(second.status_code, 202)

            first_job = self._wait_for_job(first.json()["job_id"])
            second_job = self._wait_for_job(second.json()["job_id"])

        self.assertEqual(first_job["status"], "succeeded")
        self.assertEqual(second_job["status"], "succeeded")
        self.assertNotEqual(first_job["note_id"], second_job["note_id"])
        self.assertNotEqual(first_job["output_dir"], second_job["output_dir"])
        self.assertTrue(first_job["note_id"].endswith(first.json()["job_id"]))
        self.assertTrue(second_job["note_id"].endswith(second.json()["job_id"]))

        first_package = resolve_project_path(first_job["package_path"])
        second_package = resolve_project_path(second_job["package_path"])
        self.assertTrue(first_package.exists())
        self.assertTrue(second_package.exists())
        self.assertNotEqual(first_package, second_package)
        self._cleanup_dirs.append(resolve_project_path(first_job["output_dir"]))
        self._cleanup_dirs.append(resolve_project_path(second_job["output_dir"]))

    def test_package_endpoint_rejects_invalid_note_id(self):
        response = self.client.get("/api/nail/notes/..%2F..%2Fetc%2Fpasswd/package")
        self.assertIn(response.status_code, (400, 404))

        response = self.client.get("/api/nail/notes/nail_bad$id/package")
        self.assertEqual(response.status_code, 400)

    def test_request_validation_rejects_invalid_bounds(self):
        response = self.client.post(
            "/api/nail/notes",
            json={"brief": "test", "generate_images": False, "max_workers": 3},
        )
        self.assertEqual(response.status_code, 422)

        response = self.client.post(
            "/api/nail/notes",
            json={"brief": "test", "generate_images": False, "quality": "ultra"},
        )
        self.assertEqual(response.status_code, 422)

        response = self.client.post(
            "/api/nail/notes",
            json={"brief": "test", "generate_images": False, "aspect": "2:5"},
        )
        self.assertEqual(response.status_code, 422)

        response = self.client.post(
            "/api/nail/notes",
            json={"brief": "test", "generate_images": False, "style_id": "../bad"},
        )
        self.assertEqual(response.status_code, 422)

    def test_job_store_concurrent_updates_are_safe(self):
        import threading

        job_store.create_job("job_concurrent", payload={"brief": "x"})

        failures = []

        def worker(index):
            try:
                job_store.update_job("job_concurrent", status="running", note_id="note_{index}".format(index=index))
                job = job_store.get_job("job_concurrent")
                self.assertIsNotNone(job)
            except Exception as exc:
                failures.append(exc)

        threads = [threading.Thread(target=worker, args=(index,)) for index in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(failures, [])
        job = job_store.get_job("job_concurrent")
        self.assertIsNotNone(job)
        self.assertEqual(job["job_id"], "job_concurrent")
