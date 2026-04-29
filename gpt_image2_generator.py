#!/usr/bin/env python3
"""
GPT-Image-2 图片生成器
支持 OpenAI-compatible provider 的图片生成流程
使用 curl subprocess 避免 hermes 环境 http.client 连接超时问题
"""

import os
import json
import time
import subprocess
import base64
from datetime import datetime
from pathlib import Path

from project_paths import OUTPUT_DIR, to_project_relative
from src.llm_provider import get_image_settings


def _curl_post(url: str, api_key: str, data: dict, timeout: int = 120) -> dict:
    """
    使用 curl 发送 POST 请求，避免 hermes 环境 http.client 超时问题
    
    Args:
        url: 完整 URL
        api_key: Bearer token
        data: JSON 数据体
        timeout: 超时秒数
    
    Returns:
        dict: JSON 响应
    """
    # 构建 curl 命令
    cmd = [
        "curl", "-s", "--max-time", str(timeout),
        "-X", "POST", url,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data, ensure_ascii=False),
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=False,  # 返回 bytes
        timeout=timeout + 5,
    )
    
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
        raise RuntimeError(f"curl failed: returncode={result.returncode}, stderr={stderr[:500]}")
    
    raw = result.stdout
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from API (len={len(raw)}): {e}, raw={raw[:500]}")


def _post_json(base_url: str, path: str, api_key: str, data: dict, timeout: int = 120):
    """POST JSON 到 API（使用 curl）"""
    full_url = f"{base_url}{path}"
    return _curl_post(full_url, api_key, data, timeout=timeout)


def _get_bytes_via_curl(url: str, headers: dict = None, timeout: int = 60) -> bytes:
    """使用 curl GET 字节流"""
    cmd = [
        "curl", "-s", "--max-time", str(timeout),
        "-X", "GET", url,
    ]
    if headers:
        for k, v in headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
    
    result = subprocess.run(cmd, capture_output=True, text=False, timeout=timeout + 5)
    if result.returncode != 0:
        raise RuntimeError(f"curl GET failed: {result.returncode}")
    return result.stdout


def _get_json(base_url: str, path: str, api_key: str, timeout: int = 60):
    """GET JSON from API."""
    full_url = f"{base_url}{path}"
    cmd = [
        "curl", "-s", "--max-time", str(timeout),
        "-X", "GET", full_url,
        "-H", f"Authorization: Bearer {api_key}",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=False,
        timeout=timeout + 5,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
        raise RuntimeError(f"curl GET json failed: returncode={result.returncode}, stderr={stderr[:500]}")

    raw = result.stdout
    try:
        return json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON from API (len={len(raw)}): {e}, raw={raw[:500]}")


def require_api_key(api_key: str = None) -> str:
    """Return the active provider API key or fail with a clear message."""
    resolved = api_key or get_image_settings()["api_key"]
    if not resolved:
        raise RuntimeError(
            "Missing image provider API key. Configure the active LLMProvider first."
        )
    return resolved


def get_api_base() -> str:
    settings = get_image_settings()
    return settings["api_base"]


def get_image_model() -> str:
    settings = get_image_settings()
    return settings["model"]


def _convert_size(size: str) -> str:
    """
    将比例格式转换为像素尺寸格式
    OpenAI-compatible images endpoint 常见使用 WIDTHxHEIGHT 格式如 '1024x1024'
    比例格式: '1:1', '16:9', '9:16', '3:4' 等
    """
    # 如果已经是像素格式，直接返回
    if 'x' in size:
        return size
    
    aspect_map = {
        '1:1': '1024x1024',
        '16:9': '1280x720',
        '9:16': '720x1280',
        '4:3': '1024x768',
        '3:4': '768x1024',
        '21:9': '1680x720',
        '9:21': '720x1680',
        '2:1': '1024x512',
        '1:2': '512x1024',
    }
    return aspect_map.get(size, '1024x1024')


def submit_task(prompt: str, size: str = "1:1", api_key: str = None):
    """
    提交图片生成任务
    
    Args:
        prompt: 图片描述
        size: 图片比例 - "1:1", "16:9", "9:16", "4:3", "3:4", etc.
                  或像素尺寸如 "1024x1024"
        api_key: API Key
    
    Returns:
        dict: 包含 task_id（异步模式）或直接结果（同步模式）
    """
    api_key = require_api_key(api_key)
    
    # 转换尺寸格式
    pixel_size = _convert_size(size)
    
    data = {
        "model": get_image_model(),
        "prompt": prompt,
        "n": 1,
        "size": pixel_size
    }
    
    print(f"   📤 提交任务...")
    print(f"   📝 Prompt: {prompt[:60]}...")
    print(f"   📐 Size: {size} → {pixel_size}")
    
    result = _post_json(get_api_base(), "/images/generations", api_key, data, timeout=120)
    
    # 兼容同步返回：直接返回 b64_json 或 url
    if "data" in result and isinstance(result["data"], list) and len(result["data"]) > 0:
        item = result["data"][0]
        if "task_id" in item:
            # 异步模式（原始 apimart.ai）
            task_id = item["task_id"]
            print(f"   ✅ 任务已提交: {task_id}")
            return {"success": True, "task_id": task_id, "mode": "async"}
        elif "b64_json" in item or "url" in item:
            # 同步模式
            print(f"   ✅ 同步返回，直接生成完成")
            return {"success": True, "data": result, "mode": "sync"}
    
    # 旧版 apimart 格式
    if result.get("code") == 200:
        task_id = result["data"][0]["task_id"]
        print(f"   ✅ 任务已提交: {task_id}")
        return {"success": True, "task_id": task_id, "mode": "async"}
    
    error_msg = result.get("error", {}).get("message", str(result.get("error", "Unknown error")))
    print(f"   ❌ 提交失败: {error_msg}")
    return {"success": False, "error": error_msg}


def query_task(task_id: str, api_key: str = None):
    """
    查询任务状态
    
    Returns:
        dict: 任务状态和结果
    """
    api_key = require_api_key(api_key)
    
    result = _get_json(get_api_base(), f"/tasks/{task_id}", api_key, timeout=30)
    return result


def save_base64_image(b64_data: str, save_path: str) -> str:
    """将 base64 数据保存为图片文件"""
    print(f"   💾 保存 base64 图片...")
    img_data = base64.b64decode(b64_data)
    with open(save_path, "wb") as f:
        f.write(img_data)
    size = os.path.getsize(save_path)
    print(f"   ✅ 已保存: {save_path} ({size:,} bytes)")
    return save_path


def download_image(image_url: str, save_path: str) -> str:
    """下载图片到本地（使用 curl）"""
    print(f"   📥 下载图片...")
    raw = _get_bytes_via_curl(image_url, timeout=60)
    with open(save_path, "wb") as f:
        f.write(raw)
    size = os.path.getsize(save_path)
    print(f"   ✅ 已下载: {save_path} ({size:,} bytes)")
    return save_path


def generate_image(prompt: str, size: str = "1:1", save_dir: str = None, 
                   api_key: str = None):
    """
    完整的图片生成流程（提交 + 轮询 + 下载）
    
    Returns:
        dict: 完整的生成结果
    """
    api_key = require_api_key(api_key)
    save_dir = save_dir or os.environ.get("PICTURE_SAVE_DIR", str(OUTPUT_DIR / "gpt_image2"))
    os.makedirs(save_dir, exist_ok=True)
    
    # 1. 提交任务
    submit_result = submit_task(prompt, size, api_key)
    
    if not submit_result.get("success"):
        return {"status": "failed", "error": submit_result.get("error")}
    
    mode = submit_result.get("mode")
    
    if mode == "sync":
        # 同步模式：直接提取 b64_json 或 url
        data = submit_result["data"]
        item = data["data"][0]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if "b64_json" in item:
            filename = f"sync_{timestamp}.png"
            filepath = os.path.join(save_dir, filename)
            save_base64_image(item["b64_json"], filepath)
            return {
                "status": "success",
                "mode": "sync",
                "local_path": filepath,
                "image_data": item["b64_json"],
                "usage": data.get("usage", {}),
            }
        elif "url" in item:
            filename = f"sync_{timestamp}.png"
            filepath = os.path.join(save_dir, filename)
            download_image(item["url"], filepath)
            return {
                "status": "success",
                "mode": "sync",
                "local_path": filepath,
                "url": item["url"],
            }
    
    # 2. 异步模式：轮询等待
    task_id = submit_result["task_id"]
    print(f"\n   🔄 开始轮询任务: {task_id}")
    
    max_wait = 300  # 5分钟
    start_time = time.time()
    poll_interval = 2
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            return {"status": "timeout", "task_id": task_id}
        
        result = query_task(task_id, api_key)
        
        task_data = result.get("data", result)
        status = task_data.get("status", "")
        print(f"   ⏳ 状态: {status} ({int(elapsed)}s)")
        
        if status == "completed":
            result_data = task_data.get("result", {}) if isinstance(task_data, dict) else {}
            images = result_data.get("images") or []
            first = images[0] if images else {}
            b64_json = task_data.get("b64_json")
            image_url = None
            if isinstance(first, dict):
                url_value = first.get("url")
                if isinstance(url_value, list) and url_value:
                    image_url = url_value[0]
                elif isinstance(url_value, str):
                    image_url = url_value
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if b64_json:
                filename = f"async_{timestamp}.png"
                filepath = os.path.join(save_dir, filename)
                save_base64_image(b64_json, filepath)
                return {
                    "status": "success",
                    "mode": "async",
                    "local_path": filepath,
                    "image_data": b64_json,
                    "usage": result.get("usage", {}),
                }
            elif image_url:
                filename = f"async_{timestamp}.png"
                filepath = os.path.join(save_dir, filename)
                download_image(image_url, filepath)
                return {
                    "status": "success",
                    "mode": "async",
                    "local_path": filepath,
                    "url": image_url,
                    "actual_time": task_data.get("actual_time"),
                }
        
        elif status in ("failed", "error"):
            return {"status": status, "task_id": task_id, "result": result}
        
        time.sleep(poll_interval)
        poll_interval = min(poll_interval * 1.5, 10)


if __name__ == "__main__":
    import sys
    
    prompt = sys.argv[1] if len(sys.argv) > 1 else "a cute cat"
    size = sys.argv[2] if len(sys.argv) > 2 else "1:1"
    
    result = generate_image(prompt, size)
    print("\n" + "="*50)
    print("生成结果:", result["status"])
    if result["status"] == "success":
        print("图片路径:", result["local_path"])
