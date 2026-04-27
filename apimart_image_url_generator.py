import os
import json
import time
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any

import requests


API_BASE = os.getenv("APIMART_API_BASE", "https://api.apimart.ai")


def get_api_key() -> str:
    api_key = (
        os.getenv("APIMART_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("API_KEY")
    )
    if not api_key:
        raise RuntimeError("Missing API key env. Tried APIMART_API_KEY, OPENAI_API_KEY, API_KEY")
    return api_key


def upload_reference_image(reference_image_path: str) -> str:
    api_key = get_api_key()
    path = Path(reference_image_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Reference image not found: {path}")

    url = f"{API_BASE}/v1/uploads/images"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    content_type = mimetypes.guess_type(str(path))[0] or "image/png"

    with open(path, "rb") as f:
        files = {
            "file": (path.name, f, content_type),
        }
        response = requests.post(
            url,
            headers=headers,
            files=files,
            timeout=(30, 180),
        )

    response.raise_for_status()
    data = response.json()

    image_url = data.get("url")
    if not image_url:
        raise RuntimeError(f"Upload response has no url: {json.dumps(data, ensure_ascii=False)}")

    return image_url


def create_image_generation_task(
    prompt: str,
    image_url: str,
    model: str = "gpt-image-2",
    size: str = "3:4",
    resolution: str = "1k",
    n: int = 1,
    official_fallback: Optional[bool] = None,
) -> str:
    api_key = get_api_key()

    url = f"{API_BASE}/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "image_urls": [image_url],
        "size": size,
        "resolution": resolution,
        "n": n,
    }

    if official_fallback is not None:
        payload["official_fallback"] = official_fallback

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=(30, 180),
    )

    response.raise_for_status()
    data = response.json()

    task_id = None

    if isinstance(data.get("data"), list) and data["data"]:
        task_id = data["data"][0].get("task_id") or data["data"][0].get("id")
    elif isinstance(data.get("data"), dict):
        task_id = data["data"].get("task_id") or data["data"].get("id")
    else:
        task_id = data.get("task_id") or data.get("id")

    if not task_id:
        raise RuntimeError(f"Generation response has no task_id: {json.dumps(data, ensure_ascii=False)}")

    return task_id


def get_task(task_id: str) -> Dict[str, Any]:
    api_key = get_api_key()

    url = f"{API_BASE}/v1/tasks/{task_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=(30, 60),
    )

    response.raise_for_status()
    return response.json()


def extract_result_url(task_data: Dict[str, Any]) -> Optional[str]:
    data = task_data.get("data", task_data)

    if not isinstance(data, dict):
        return None

    result = data.get("result")
    if not isinstance(result, dict):
        return None

    images = result.get("images")
    if not images:
        return None

    first = images[0]

    if isinstance(first, dict):
        url = first.get("url")
        if isinstance(url, list) and url:
            return url[0]
        if isinstance(url, str):
            return url

    if isinstance(first, str):
        return first

    return None


def wait_for_task_result(
    task_id: str,
    initial_delay_seconds: int = 15,
    poll_interval_seconds: int = 5,
    max_wait_seconds: int = 300,
) -> Dict[str, Any]:
    start = time.time()

    if initial_delay_seconds > 0:
        time.sleep(initial_delay_seconds)

    while True:
        task_data = get_task(task_id)
        data = task_data.get("data", task_data)

        status = data.get("status") if isinstance(data, dict) else None

        if status in ("completed", "succeeded", "success"):
            return task_data

        if status in ("failed", "error"):
            raise RuntimeError(f"Task failed: {json.dumps(task_data, ensure_ascii=False, indent=2)}")

        if time.time() - start > max_wait_seconds:
            raise TimeoutError(f"Task polling timeout after {max_wait_seconds}s: {task_id}")

        time.sleep(poll_interval_seconds)


def generate_image_with_reference(
    prompt: str,
    reference_image_path: str,
    model: str = "gpt-image-2",
    size: str = "3:4",
    resolution: str = "1k",
    n: int = 1,
    official_fallback: Optional[bool] = None,
) -> Dict[str, Any]:
    reference_image_url = upload_reference_image(reference_image_path)

    task_id = create_image_generation_task(
        prompt=prompt,
        image_url=reference_image_url,
        model=model,
        size=size,
        resolution=resolution,
        n=n,
        official_fallback=official_fallback,
    )

    task_data = wait_for_task_result(task_id)
    result_url = extract_result_url(task_data)

    if not result_url:
        raise RuntimeError(f"Completed task has no result image url: {json.dumps(task_data, ensure_ascii=False)}")

    return {
        "status": "success",
        "url": result_url,
        "task_id": task_id,
        "reference_image_url": reference_image_url,
        "model": model,
        "size": size,
        "resolution": resolution,
        "raw": task_data,
    }
