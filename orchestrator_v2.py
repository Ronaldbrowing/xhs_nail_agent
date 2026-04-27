from pathlib import Path
from datetime import datetime
import json
import os

from design_compiler import compile_prompt_package
from gpt_image2_generator import generate_image
from case_library import (
    add_case,
    get_case_image_path,
)

OUTPUT_DIR = Path.home() / ".hermes" / "agents" / "multi-agent-image" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _normalize_generation_result(raw):
    """
    把不同格式的图片生成返回值统一成：
    {
        "success": bool,
        "filepath": str | None,
        "url": str | None,
        "raw": 原始返回
    }
    """
    import os

    if isinstance(raw, str):
        return {
            "success": bool(raw and os.path.exists(raw)),
            "filepath": raw,
            "url": None,
            "raw": raw,
        }

    if not isinstance(raw, dict):
        return {
            "success": False,
            "filepath": None,
            "url": None,
            "raw": raw,
        }

    filepath = (
        raw.get("filepath")
        or raw.get("path")
        or raw.get("local_path")
        or raw.get("file")
        or raw.get("image_path")
    )

    url = (
        raw.get("url")
        or raw.get("image_url")
        or raw.get("download_url")
    )

    success = bool(
        raw.get("success")
        or raw.get("ok")
        or raw.get("status") == "success"
        or raw.get("status") == "completed"
        or (filepath and os.path.exists(filepath))
    )

    normalized = dict(raw)
    normalized["success"] = success
    normalized["filepath"] = filepath
    normalized["url"] = url
    normalized["raw"] = raw

    return normalized



def log(role: str, emoji: str, message: str):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {emoji} [{role}] {message}")


def step1_prompt_engineer(user_input: str) -> dict:
    log("Prompt工程师", "📝", "接收用户需求，开始分析...")
    try:
        # 当前版本保持轻量，直接透传为 optimized_brief。
        # 如果后续要接文本 LLM，可在这里扩展。
        result = {
            "core_subject": user_input,
            "optimized_brief": user_input,
            "mode": "fallback",
            "reasoning": "回退模式",
        }
        log("Prompt工程师", "📝", "✅ 分析完成 (回退模式)")
        return result
    except Exception:
        result = {
            "core_subject": user_input,
            "optimized_brief": user_input,
            "mode": "fallback",
            "reasoning": "回退模式",
        }
        log("Prompt工程师", "📝", "✅ 分析完成 (回退模式)")
        return result


def step2_style_scout(brief: str, user_input: str = "") -> dict:
    log("风格研究员", "🎨", "分析最佳设计参数...")
    try:
        # 当前版本先保守默认，避免再次覆盖上游强制参数。
        result = {
            "task": "poster",
            "direction": "balanced",
            "aspect": "1:1",
            "quality": "final",
            "reasoning": "默认参数",
        }
        log("风格研究员", "🎨", f"⚠️ 回退到默认参数")
        return result
    except Exception:
        result = {
            "task": "poster",
            "direction": "balanced",
            "aspect": "1:1",
            "quality": "final",
            "reasoning": "默认参数",
        }
        log("风格研究员", "🎨", f"⚠️ 回退到默认参数")
        return result


def step3_image_generator(
    brief: str,
    task: str,
    direction: str,
    aspect: str,
    quality: str,
    reference_image: str = None,
) -> dict:
    log("图片生成引擎", "🖼️", "启动设计编译 + 图片生成...")
    log("图片生成引擎", "🖼️", "   ① 调用内置编译器生成 Prompt...")

    package = compile_prompt_package(
        brief=brief,
        task=task,
        direction=direction,
        aspect=aspect,
        quality=quality,
    )
    final_prompt = package.get("final_prompt") or package.get("prompt") or brief

    log("图片生成引擎", "🖼️", f"   ✅ Prompt 编译完成 ({len(final_prompt)} 字符)")
    log("图片生成引擎", "🖼️", "   ② 调用 GPT-Image-2 API...")

    save_dir = str(OUTPUT_DIR)

    raw_gen = generate_image(
        prompt=final_prompt,
        size=aspect,
        save_dir=save_dir,
    )

    gen = _normalize_generation_result(raw_gen)

    if not gen.get("success"):
        return {
            "status": "failed",
            "error": gen.get("error", "Image generation failed"),
            "final_prompt": final_prompt,
            "style_params": {
                "task": task,
                "direction": direction,
                "aspect": aspect,
                "quality": quality,
            },
        }

    result = {
        "status": "success",
        "filepath": gen.get("filepath"),
        "url": gen.get("url"),
        "task_id": gen.get("task_id"),
        "final_prompt": final_prompt,
        "style_params": {
            "task": task,
            "direction": direction,
            "aspect": aspect,
            "quality": quality,
        },
        "used_reference": bool(reference_image),
    }

    if "actual_time" in gen:
        result["actual_time"] = gen["actual_time"]

    return result


def step4_qa(generation: dict) -> dict:
    log("质量审核员", "✅", "评估中...")
    # 当前保持轻量规则制；后续可接视觉评估模型。
    score = 9.0 if generation.get("status") == "success" else 0.0
    approval = generation.get("status") == "success"
    verdict = "PASS" if approval else "FAIL"
    log("质量审核员", "✅", f"   ✅ {verdict} ({score}/10)" if approval else f"   ❌ {verdict} ({score}/10)")
    return {
        "verdict": verdict,
        "score": score,
        "approval": approval,
    }


def step5_metadata(
    user_input: str,
    prompt_data: dict,
    style_data: dict,
    generation: dict,
    qa: dict,
    workflow_diagnostics: dict = None,
    model_usage: dict = None,
    dna_summary: str = None,
) -> str:
    log("档案管理员", "📁", "归档中...")

    workflow_diagnostics = workflow_diagnostics or {}
    model_usage = model_usage or {}

    archive = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "prompt_analysis": prompt_data,
        "style_params": style_data,
        "workflow_diagnostics": workflow_diagnostics,
        "model_usage": model_usage,
        "generation": generation,
        "quality_check": qa,
        "dna_summary": dna_summary,
    }

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    meta_path = OUTPUT_DIR / f"{ts}_archive.json"

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)

    log("档案管理员", "📁", f"   ✅ {meta_path.name}")
    return str(meta_path)


def run(
    user_input: str,
    use_reference: bool = True,
    task: str = None,
    direction: str = None,
    aspect: str = None,
    quality: str = None,
    case_id: str = None,
    precompiled_brief: bool = False,
    dna_summary: str = None,
) -> dict:
    """
    🚀 主工作流入口（案例库版）
    """

    print("=" * 70)
    print("🎨 Multi-Agent Image - 多 Agent 协作工作流 v2")
    print("=" * 70)
    print(f"📝 需求: {user_input}")

    prompt_analysis_mode = "unknown"
    style_params_mode = "unknown"
    forced_params_applied = False

    stage_status = {
        "prompt_ok": False,
        "style_ok": False,
        "generation_ok": False,
        "quality_ok": False,
        "archive_ok": False,
        "case_library_ok": False,
    }

    model_usage = {
        "text_llm_calls_attempted": 0,
        "text_llm_calls_succeeded": 0,
        "image_generation_calls": 0,
        "image_generation_succeeded": 0,
        "quality_check_calls": 0,
        "quality_check_model_based": False,
    }

    if task:
        print(f"⚙️  强制参数: task={task} direction={direction} aspect={aspect} quality={quality}")
    print()

    # Step 1: Prompt 工程师
    if precompiled_brief:
        prompt_data = {
            "core_subject": user_input,
            "optimized_brief": user_input,
            "mode": "bypassed",
            "reasoning": "upstream_precompiled",
        }
        brief = user_input
        prompt_analysis_mode = "bypassed"
        stage_status["prompt_ok"] = True
        log("Prompt工程师", "📝", "⏭️ 已跳过，上游已提供预编译 brief")
    else:
        model_usage["text_llm_calls_attempted"] += 1
        prompt_data = step1_prompt_engineer(user_input)
        brief = prompt_data.get("optimized_brief", user_input)
        if prompt_data.get("mode") == "fallback" or prompt_data.get("reasoning") == "回退模式":
            prompt_analysis_mode = "fallback"
        else:
            prompt_analysis_mode = prompt_data.get("mode", "primary")
            model_usage["text_llm_calls_succeeded"] += 1
        stage_status["prompt_ok"] = True
    print()

    # Step 2: 风格研究员（如果强制参数则跳过）
    if task and direction and aspect:
        final_task = task
        final_direction = direction
        final_aspect = aspect
        final_quality = quality or "final"
        style_data = {
            "task": final_task,
            "direction": final_direction,
            "aspect": final_aspect,
            "quality": final_quality,
            "reasoning": "强制参数",
        }
        style_params_mode = "forced"
        forced_params_applied = True
        stage_status["style_ok"] = True
        log("风格研究员", "🎨", f"✅ 使用强制参数: {final_task}/{final_direction}/{final_aspect}/{final_quality}")
    else:
        style_data = step2_style_scout(brief, user_input)
        final_task = style_data.get("task", "poster")
        final_direction = style_data.get("direction", "balanced")
        final_aspect = style_data.get("aspect", "1:1")
        final_quality = style_data.get("quality", "final")
        style_params_mode = "primary"
        stage_status["style_ok"] = True
    print()

    # 案例库 / 参考图
    reference_image = None
    if use_reference and case_id:
        reference_image = get_case_image_path(case_id, final_task)
        if reference_image:
            log("案例库", "📚", f"使用指定案例: {case_id} → {Path(reference_image).name}")
        else:
            log("案例库", "📚", f"⚠️ 案例 {case_id} 不存在，将全新生成")
    elif use_reference:
        reference_image = None
        log("案例库", "📚", "当前版本未启用自动选案例，改为全新生成")
    else:
        log("案例库", "📚", "不参考案例，全新生成")
    print()

    # DNA 轻量注入
    if dna_summary:
        brief = brief.rstrip() + "\n\n【参考图DNA摘要】\n" + str(dna_summary).strip()

    # Step 3: 图片生成
    print(f"[FINAL PARAMS] task={final_task} direction={final_direction} aspect={final_aspect} quality={final_quality}")
    if dna_summary:
        print(f"[DNA] 已注入参考图摘要，长度={len(str(dna_summary))}")

    model_usage["image_generation_calls"] += 1
    generation = step3_image_generator(
        brief=brief,
        task=final_task,
        direction=final_direction,
        aspect=final_aspect,
        quality=final_quality,
        reference_image=reference_image,
    )
    print()

    if generation.get("status") != "success":
        print("=" * 70)
        print("❌ 生成失败")
        print("=" * 70)
        return {
            "success": False,
            "stage": "generation",
            "error": generation.get("error"),
            "workflow_diagnostics": {
                "prompt_analysis_mode": prompt_analysis_mode,
                "style_params_mode": style_params_mode,
                "forced_params_applied": forced_params_applied,
                "stage_status": stage_status,
                "model_usage": model_usage,
                "precompiled_brief": precompiled_brief,
                "dna_summary_included": bool(dna_summary),
            },
        }

    stage_status["generation_ok"] = True
    model_usage["image_generation_succeeded"] += 1

    # Step 4: QA
    model_usage["quality_check_calls"] += 1
    qa = step4_qa(generation)
    stage_status["quality_ok"] = bool(qa.get("approval"))
    print()

    workflow_diagnostics = {
        "prompt_analysis_mode": prompt_analysis_mode,
        "style_params_mode": style_params_mode,
        "forced_params_applied": forced_params_applied,
        "final_params": {
            "task": final_task,
            "direction": final_direction,
            "aspect": final_aspect,
            "quality": final_quality,
        },
        "stage_status": stage_status,
        "precompiled_brief": precompiled_brief,
        "dna_summary_included": bool(dna_summary),
    }

    # Step 5: 档案
    try:
        meta_path = step5_metadata(
            user_input,
            prompt_data,
            style_data,
            generation,
            qa,
            workflow_diagnostics=workflow_diagnostics,
            model_usage=model_usage,
            dna_summary=dna_summary,
        )
        stage_status["archive_ok"] = True
    except Exception as e:
        meta_path = None
        print(f"[WARN] archive failed: {e}")
    print()

    # 案例库保存
    try:
        case_meta = {
            "brief": user_input,
            "prompt": generation.get("final_prompt", ""),
            "params": {
                "task": final_task,
                "direction": final_direction,
                "aspect": final_aspect,
                "quality": final_quality,
            },
            "rating": qa.get("score", 0),
        }
        add_case(
            image_path=generation["filepath"],
            metadata=case_meta,
            task=final_task,
            tags=[],
        )
        stage_status["case_library_ok"] = True
        print("[案例库] ✅ 案例已保存")
    except Exception as e:
        print(f"[案例库] ⚠️ 保存失败: {e}")

    print("=" * 70)
    print("✅ 任务完成!")
    print("=" * 70)
    print("📁 文件:")
    print(f"   🖼️  图片: {generation['filepath']}")
    if meta_path:
        print(f"   📝 档案: {meta_path}")
    else:
        print(f"   📝 档案: 未成功写入")
    print("📊 质量:")
    print(f"   ⭐ 评分: {qa['score']}/10")

    if reference_image:
        print(f"   📎 参考: {Path(reference_image).name}")
    else:
        print(f"   🆕 全新生成")

    print("⚙️  参数:")
    print(f"   {final_task} | {final_direction} | {final_aspect}")

    url = generation.get("url", "")
    if url:
        print(f"🔗 {url[:50]}...")
        print("⚠️  链接24h有效")

    return {
        "success": True,
        "filepath": generation["filepath"],
        "url": generation.get("url"),
        "score": qa.get("score"),
        "params": {
            "task": final_task,
            "direction": final_direction,
            "aspect": final_aspect,
            "quality": final_quality,
        },
        "used_reference": bool(reference_image),
        "workflow_diagnostics": {
            "prompt_analysis_mode": prompt_analysis_mode,
            "style_params_mode": style_params_mode,
            "forced_params_applied": forced_params_applied,
            "stage_status": stage_status,
            "model_usage": model_usage,
            "precompiled_brief": precompiled_brief,
            "dna_summary_included": bool(dna_summary),
        },
        "partial_failure": not stage_status["archive_ok"] or not stage_status["case_library_ok"],
        "failed_stage": (
            None if stage_status["archive_ok"] and stage_status["case_library_ok"]
            else "archive_or_case_library"
        ),
    }