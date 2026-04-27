import os
import sys
import json
import time
import mimetypes
from pathlib import Path

import requests


API_BASE = os.getenv("APIMART_API_BASE", "https://api.apimart.ai")


def get_api_key():
    api_key = (
        os.getenv("APIMART_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("API_KEY")
    )
    if not api_key:
        raise RuntimeError("Missing API key env. Tried APIMART_API_KEY, OPENAI_API_KEY, API_KEY")
    return api_key


def upload_image(image_path: str) -> str:
    api_key = get_api_key()
    path = Path(image_path).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Reference image not found: {path}")

    url = f"{API_BASE}/v1/uploads/images"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    content_type = mimetypes.guess_type(str(path))[0] or "image/png"

    print("UPLOAD", url)
    print("IMAGE", str(path))
    print("MIME", content_type)

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

    print("UPLOAD STATUS:", response.status_code)
    print("UPLOAD TEXT:")
    print(response.text[:2000])

    response.raise_for_status()
    data = response.json()

    image_url = data.get("url")
    if not image_url:
        raise RuntimeError(f"Upload response has no url: {data}")

    print("UPLOADED URL:", image_url)
    return image_url


def create_generation(image_url: str, prompt: str):
    api_key = get_api_key()

    url = f"{API_BASE}/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "image_urls": [image_url],
        "size": "3:4",
        "resolution": "1k",
        "n": 1,
    }

    print("GENERATE", url)
    print("PAYLOAD:")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=(30, 180),
    )

    print("GENERATE STATUS:", response.status_code)
    print("GENERATE TEXT:")
    print(response.text[:4000])

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
        raise RuntimeError(f"Generation response has no task_id: {data}")

    print("TASK_ID:", task_id)
    return task_id


def get_task(task_id: str):
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

    print("TASK STATUS:", response.status_code)
    print("TASK TEXT:")
    print(response.text[:4000])

    response.raise_for_status()
    return response.json()


def extract_result_url(task_data):
    data = task_data.get("data", task_data)

    result = data.get("result") if isinstance(data, dict) else None
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


def wait_for_result(task_id: str, max_wait_seconds: int = 240):
    start = time.time()

    print("WAIT 15s before first poll...")
    time.sleep(15)

    while True:
        task_data = get_task(task_id)

        data = task_data.get("data", task_data)
        status = data.get("status") if isinstance(data, dict) else None

        print("CURRENT STATUS:", status)

        if status in ("completed", "succeeded", "success"):
            result_url = extract_result_url(task_data)
            print("RESULT URL:", result_url)
            return task_data

        if status in ("failed", "error"):
            raise RuntimeError(f"Task failed: {json.dumps(task_data, ensure_ascii=False, indent=2)}")

        if time.time() - start > max_wait_seconds:
            raise TimeoutError(f"Task polling timeout after {max_wait_seconds}s: {task_id}")

        time.sleep(5)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 probe_image_url_generation.py <reference_image>")
        sys.exit(1)

    reference_image = sys.argv[1]

    prompt = (
        "基于参考图继续生成一张同风格的小红书美甲封面。"
        "保持夏日蓝色猫眼短甲、清透显白、手部自然、指甲清晰、封面式构图、干净留白。"
        "不要直接生成文字，不要机械复制原图。"
    )

    uploaded_url = upload_image(reference_image)
    task_id = create_generation(uploaded_url, prompt)
    final = wait_for_result(task_id)

    print("FINAL:")
    print(json.dumps(final, ensure_ascii=False, indent=2))
