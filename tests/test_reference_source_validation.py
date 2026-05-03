import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from verticals.nail.api.app import app
from verticals.nail.service import job_store
from verticals.nail.service.schemas import NailNoteCreateRequest


@pytest.fixture
def client(monkeypatch):
    job_store.reset_jobs()
    monkeypatch.setattr("verticals.nail.api.routes._run_create_job", lambda job_id, request: None)
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_jobs():
    job_store.reset_jobs()
    yield
    job_store.reset_jobs()


def test_request_infers_reference_source_none():
    request = NailNoteCreateRequest(brief="test", generate_images=False)
    assert request.reference_source == "none"
    assert request.reference_image_path is None
    assert request.case_id is None


def test_request_infers_reference_source_local_path():
    request = NailNoteCreateRequest(
        brief="test",
        generate_images=False,
        reference_image_path="input/reference_uploads/ref_demo.png",
    )
    assert request.reference_source == "local_path"
    assert request.reference_image_path == "input/reference_uploads/ref_demo.png"


def test_request_infers_reference_source_case_id():
    request = NailNoteCreateRequest(
        brief="test",
        generate_images=False,
        case_id="case_fixture_001_nail_api",
    )
    assert request.reference_source == "case_id"
    assert request.case_id == "case_fixture_001_nail_api"


def test_request_rejects_none_with_reference_fields():
    with pytest.raises(ValueError, match="reference_source=none"):
        NailNoteCreateRequest(
            brief="test",
            generate_images=False,
            reference_source="none",
            case_id="case_fixture_001_nail_api",
        )


def test_request_rejects_local_path_without_reference_image():
    with pytest.raises(ValueError, match="requires reference_image_path"):
        NailNoteCreateRequest(
            brief="test",
            generate_images=False,
            reference_source="local_path",
        )


def test_request_rejects_case_id_without_case_id():
    with pytest.raises(ValueError, match="requires case_id"):
        NailNoteCreateRequest(
            brief="test",
            generate_images=False,
            reference_source="case_id",
        )


def test_api_accepts_inferred_local_path(client):
    response = client.post(
        "/api/nail/notes",
        json={
            "brief": "test",
            "generate_images": False,
            "reference_image_path": "input/reference_uploads/ref_demo.png",
        },
    )
    assert response.status_code == 202
    payload = response.json()
    job = job_store.get_job(payload["job_id"])
    assert job is not None
    assert job["payload"]["reference_source"] == "local_path"


def test_api_accepts_inferred_case_id_and_persists_source(client, monkeypatch):
    fake_service = Mock()
    fake_service.get_case.return_value = {
        "case_id": "case_fixture_001_nail_api",
        "vertical": "nail",
        "image_path": "case_library/poster/case_fixture_001_nail_api/image.png",
    }
    monkeypatch.setattr("verticals.nail.api.routes._get_case_service", lambda: fake_service)

    response = client.post(
        "/api/nail/notes",
        json={
            "brief": "test",
            "generate_images": False,
            "case_id": "case_fixture_001_nail_api",
        },
    )
    assert response.status_code == 202
    payload = response.json()
    job = job_store.get_job(payload["job_id"])
    assert job is not None
    assert job["payload"]["reference_source"] == "case_id"
    fake_service.get_case.assert_called_once_with("nail", "case_fixture_001_nail_api")


def test_api_rejects_unknown_case_id(client, monkeypatch):
    fake_service = Mock()
    fake_service.get_case.side_effect = FileNotFoundError("case_id not found: case_missing")
    monkeypatch.setattr("verticals.nail.api.routes._get_case_service", lambda: fake_service)

    response = client.post(
        "/api/nail/notes",
        json={
            "brief": "test",
            "generate_images": False,
            "reference_source": "case_id",
            "case_id": "case_missing",
        },
    )
    assert response.status_code == 404
    assert "case_id not found or has no image" in response.json()["detail"]


def test_api_rejects_reference_source_mutual_exclusion(client):
    response = client.post(
        "/api/nail/notes",
        json={
            "brief": "test",
            "generate_images": False,
            "reference_source": "case_id",
            "case_id": "case_fixture_001_nail_api",
            "reference_image_path": "input/reference_uploads/ref_demo.png",
        },
    )
    assert response.status_code == 422
