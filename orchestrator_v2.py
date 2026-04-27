from pathlib import Path
from datetime import datetime
import json
import os

from design_compiler import compile_prompt_package
from gpt_image2_generator import generate_image
from case_library import (
    add_case,
    get_case_image_path,
    get_case_metadata,
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

def build_dna_summary_from_case_meta(case_meta: dict) -> str:
    """
    从案例 metadata 自动生成可注入 prompt 的 DNA 摘要。

    这个函数不依赖多模态模型，不读取图片本身；
    它只使用历史案例保存下来的 brief、prompt、params、tags 等文本信息。
    """
    if not case_meta:
        return None

    brief = str(case_meta.get("brief") or "").strip()
    prompt = str(case_meta.get("prompt") or "").strip()
    if "【参考图DNA摘要】" in prompt:
        prompt = prompt.split("【参考图DNA摘要】", 1)[0].strip()
    params = case_meta.get("params") or {}
    tags = case_meta.get("tags") or []
    rating = case_meta.get("rating", 0)

    text_pool = "\n".join([
        brief,
        prompt,
        " ".join(str(tag) for tag in tags),
    ])

    style_hints = []

    keyword_rules = [
        ("清透", "清透感"),
        ("透亮", "透亮质感"),
        ("玻璃", "玻璃感"),
        ("猫眼", "猫眼光泽"),
        ("珠光", "珠光反射"),
        ("渐变", "渐变过渡"),
        ("蓝", "蓝色系"),
        ("粉", "粉色系"),
        ("裸", "裸色系"),
        ("短甲", "短甲形态"),
        ("长甲", "长甲形态"),
        ("法式", "法式边缘设计"),
        ("夏日", "夏日清爽氛围"),
        ("小红书", "小红书封面风格"),
        ("封面", "封面式构图"),
        ("留白", "留白构图"),
        ("高级", "高级感"),
        ("极简", "极简风格"),
        ("甜美", "甜美风格"),
    ]

    for keyword, label in keyword_rules:
        if keyword in text_pool and label not in style_hints:
            style_hints.append(label)

    if not style_hints:
        style_hints.append("历史案例中的视觉风格、构图逻辑和质感表达")

    dna_parts = [
        "请参考历史案例的视觉 DNA，但不要机械复制原图。",
        f"历史案例主题：{brief[:160] if brief else '未记录'}",
        f"风格关键词：{'、'.join(style_hints)}",
        f"任务类型参考：{params.get('task', case_meta.get('task', 'poster'))}",
        f"画面比例参考：{params.get('aspect', '未记录')}",
        f"设计方向参考：{params.get('direction', '未记录')}",
        f"历史评分参考：{rating}",
        "继承重点：配色逻辑、材质质感、画面氛围、主体呈现方式、构图留白。",
        "变化要求：根据当前新需求重新生成，不要一比一复刻历史案例。",
    ]

    if tags:
        dna_parts.insert(4, f"案例标签：{'、'.join(str(tag) for tag in tags[:8])}")

    if prompt:
        dna_parts.append(f"历史 prompt 摘要：{prompt[:300]}")

    return "\n".join(dna_parts)


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
    effective_dna_summary = str(dna_summary).strip() if dna_summary else None
    dna_summary_source = "user" if effective_dna_summary else None

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
    if not effective_dna_summary and use_reference and case_id:
        case_meta = get_case_metadata(case_id, final_task)
        if case_meta:
            effective_dna_summary = build_dna_summary_from_case_meta(case_meta)
            dna_summary_source = "case_metadata"
            if effective_dna_summary:
                log(
                    "案例库",
                    "📚",
                    f"已从案例 {case_id} 自动生成 DNA 摘要，长度={len(effective_dna_summary)}"
                )
        else:
            log("案例库", "📚", f"⚠️ 案例 {case_id} 的 metadata 不存在，无法自动生成 DNA 摘要")

    if effective_dna_summary:
        brief = brief.rstrip() + "\n\n【参考图DNA摘要】\n" + effective_dna_summary

    # Step 3: 图片生成
    print(f"[FINAL PARAMS] task={final_task} direction={final_direction} aspect={final_aspect} quality={final_quality}")

    if effective_dna_summary:   
        print(
            f"[DNA] 已注入参考图摘要，来源={dna_summary_source}, "
            f"长度={len(effective_dna_summary)}"
        )


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
                "final_params": {
                    "task": final_task,
                    "direction": final_direction,
                    "aspect": final_aspect,
                    "quality": final_quality,
                },
                "stage_status": stage_status,
                "precompiled_brief": precompiled_brief,
                "dna_summary_included": bool(effective_dna_summary),
                "dna_summary_source": dna_summary_source,
            }
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
        "dna_summary_included": bool(effective_dna_summary),
        "dna_summary_source": dna_summary_source,
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
            dna_summary=effective_dna_summary,
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
            "dna_summary_included": bool(effective_dna_summary),
            "dna_summary_source": dna_summary_source,
        },
        "partial_failure": not stage_status["archive_ok"] or not stage_status["case_library_ok"],
        "failed_stage": (
            None if stage_status["archive_ok"] and stage_status["case_library_ok"]
            else "archive_or_case_library"
        ),
    }