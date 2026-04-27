#!/usr/bin/env python3
import os
import sys
import json
import requests
from pathlib import Path

API_BASE = "https://api.apimart.ai/v1"


def require_api_key() -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")
    return api_key


def probe_image_edit(reference_image: str, prompt: str, size: str = "3:4"):
    api_key = require_api_key()
    reference_path = Path(reference_image)

    if not reference_path.exists():
        raise FileNotFoundError(f"Reference image not found: {reference_image}")

    url = f"{API_BASE}/images/edits"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    data = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": size,
    }

    with open(reference_path, "rb") as f:
        files = {
            "image": (reference_path.name, f, "image/png"),
        }

        print("POST", url)
        print("DATA", json.dumps(data, ensure_ascii=False, indent=2))
        print("IMAGE", str(reference_path))

        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files,
            timeout=(30, 180),
        )

    print("STATUS:", response.status_code)
    print("TEXT:")
    print(response.text[:3000])

    try:
        return response.json()
    except Exception:
        return {"raw_text": response.text}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 probe_image_edit.py <reference_image>")
        sys.exit(1)

    reference_image = sys.argv[1]
    prompt = (
        "基于参考图继续生成一张同风格的小红书美甲封面。"
        "保持夏日蓝色猫眼短甲、清透显白、手部自然、指甲清晰。"
        "不要直接生成文字，不要机械复制原图。"
    )

    result = probe_image_edit(reference_image, prompt, size="1024x1536")
    print(json.dumps(result, ensure_ascii=False, indent=2))
