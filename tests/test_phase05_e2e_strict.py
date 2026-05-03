#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Phase 0.5 严格版端到端验收测试

覆盖：
A. 有效 case_id 图生图
B. 无参考图文生图
C. 无效 case_id fallback 文生图
D. archive / package / assets / history_index 一致性检查
E. 路径审计
F. record_id 唯一性检查

说明：
- 默认不强制测试“真实生成失败归档”，因为这通常需要故意打坏 API key
- 若你想额外测试失败归档，可传环境变量：
    PHASE05_FORCE_FAILURE=1
"""

import json
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from orchestrator_v2 import run
from project_paths import OUTPUT_DIR
from src.record_manager import generate_record_id

TEST_CASE_ID = "case_test_001"
TEST_BRIEF = "夏日蓝色猫眼短甲，适合黄皮，显白清透"
INVALID_CASE_ID = f"invalid_case_{uuid.uuid4().hex[:8]}"

REPORT = {
    "timestamp": datetime.now().isoformat(),
    "results": {}
}


def print_title(title: str):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def get_record_dirs():
    records_dir = OUTPUT_DIR / "records"
    if not records_dir.exists():
        return []
    return sorted(
        [p for p in records_dir.iterdir() if p.is_dir() and p.name.startswith("image_")],
        key=lambda p: p.name
    )


def get_latest_record_dir():
    dirs = get_record_dirs()
    return dirs[-1] if dirs else None


def snapshot_record_names():
    return {p.name for p in get_record_dirs()}


def get_new_record_dir(before_names: set):
    after = get_record_dirs()
    new_dirs = [p for p in after if p.name not in before_names]
    if not new_dirs:
        return None
    return sorted(new_dirs, key=lambda p: p.name)[-1]


def assert_file_exists(path_str: str):
    if not path_str:
        return False
    p = PROJECT_ROOT / path_str
    return p.exists() and p.is_file()


def load_record_bundle(record_dir: Path):
    return {
        "record_dir": record_dir,
        "note_package_path": record_dir / "note_package.json",
        "archive_path": record_dir / "archive.json",
        "note_package": read_json(record_dir / "note_package.json"),
        "archive": read_json(record_dir / "archive.json"),
        "generated_dir": record_dir / "assets" / "generated",
        "references_dir": record_dir / "assets" / "references",
    }


def check_common_record_integrity(bundle: dict):
    pkg = bundle["note_package"]
    arc = bundle["archive"]
    record_dir = bundle["record_dir"]

    checks = {}

    checks["note_package_exists"] = bundle["note_package_path"].exists()
    checks["archive_exists"] = bundle["archive_path"].exists()
    checks["record_id_match"] = pkg.get("record_id") == record_dir.name
    checks["files_package_path_match"] = (
        pkg.get("files", {}).get("package_path") == f"output/records/{record_dir.name}/note_package.json"
    )
    checks["files_archive_path_match"] = (
        pkg.get("files", {}).get("archive_path") == f"output/records/{record_dir.name}/archive.json"
    )
    checks["display_cover_present_or_failed"] = bool(
        pkg.get("display", {}).get("cover_image_path") or pkg.get("status") == "failed"
    )
    checks["pages_nonempty"] = len(pkg.get("pages", [])) == 1
    checks["archive_user_input_present"] = bool(arc.get("user_input"))
    checks["archive_generation_present"] = isinstance(arc.get("generation"), dict)
    checks["archive_quality_present"] = isinstance(arc.get("quality_check"), dict)
    return checks


def check_history_index_contains(record_id: str):
    history_path = OUTPUT_DIR / "history_index.jsonl"
    rows = read_jsonl(history_path)
    matches = [r for r in rows if r.get("record_id") == record_id]
    return history_path.exists(), rows, matches


def check_forbidden_paths():
    records_dir = OUTPUT_DIR / "records"
    forbidden = [
        "/Users/wiwi",
        "/Users/wiwi/.hermes",
        "~/.hermes",
        "multi-agent-image",
        "Path.home()",
    ]

    json_files = []
    if records_dir.exists():
        json_files.extend(records_dir.glob("**/*.json"))
        json_files.extend(records_dir.glob("**/*.jsonl"))

    bad = []
    for p in json_files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for token in forbidden:
            if token in text:
                bad.append({"file": str(p.relative_to(PROJECT_ROOT)), "token": token})

    return {
        "json_file_count": len(json_files),
        "bad_count": len(bad),
        "bad": bad[:20],
        "passed": len(bad) == 0
    }


def test_A_valid_case_img2img():
    print_title("【测试 A】有效 case_id 图生图")

    before = snapshot_record_names()

    result = run(
        user_input=TEST_BRIEF,
        use_reference=True,
        case_id=TEST_CASE_ID,
        task="poster",
        direction="balanced",
        aspect="3:4",
        quality="final",
    )

    record_dir = get_new_record_dir(before) or get_latest_record_dir()
    bundle = load_record_bundle(record_dir)
    pkg = bundle["note_package"]

    checks = {}

    checks["run_success"] = result.get("success") is True
    checks["pkg_status_success"] = pkg.get("status") == "success"
    checks["references_len_gt_0"] = len(pkg.get("references", [])) > 0

    ref = (pkg.get("references") or [{}])[0]
    page = (pkg.get("pages") or [{}])[0]

    checks["ref_source_type_case_id"] = ref.get("source_type") == "case_id"
    checks["ref_source_value_match"] = ref.get("source_value") == TEST_CASE_ID
    checks["ref_original_path_case_library"] = str(ref.get("original_path", "")).startswith("case_library/")
    checks["ref_archived_path_records"] = str(ref.get("archived_path", "")).startswith("output/records/")
    checks["ref_archived_file_exists"] = assert_file_exists(ref.get("archived_path"))

    checks["page_reference_ids_ref001"] = page.get("reference_ids") == ["ref_001"]
    checks["page_used_reference_true"] = page.get("used_reference") is True
    checks["page_generation_mode_img2img"] = page.get("generation", {}).get("mode") == "image_to_image"

    image_path = page.get("image", {}).get("path")
    checks["page_image_exists"] = assert_file_exists(image_path)
    checks["generated_assets_nonempty"] = len(list(bundle["generated_dir"].glob("*"))) > 0
    checks["references_assets_nonempty"] = len(list(bundle["references_dir"].glob("*"))) > 0

    display = pkg.get("display", {})
    checks["display_cover_matches_page_image"] = display.get("cover_image_path") == image_path
    checks["display_reference_thumb_present"] = bool(display.get("reference_thumbnail_path"))

    checks.update(check_common_record_integrity(bundle))

    history_exists, rows, matches = check_history_index_contains(pkg.get("record_id"))
    checks["history_index_exists"] = history_exists
    checks["history_index_has_record"] = len(matches) >= 1
    if matches:
        checks["history_used_reference_true"] = matches[-1].get("used_reference") is True
        checks["history_cover_matches"] = matches[-1].get("cover_image_path") == image_path
    else:
        checks["history_used_reference_true"] = False
        checks["history_cover_matches"] = False

    passed = all(checks.values())

    result_data = {
        "passed": passed,
        "record_dir": str(record_dir),
        "checks": checks,
        "result": result,
    }
    REPORT["results"]["A_valid_case_img2img"] = result_data
    print(json.dumps(result_data, ensure_ascii=False, indent=2))
    return result_data


def test_B_no_ref_txt2img():
    print_title("【测试 B】无参考图文生图")

    before = snapshot_record_names()

    result = run(
        user_input=TEST_BRIEF,
        use_reference=False,
        task="poster",
        direction="balanced",
        aspect="3:4",
        quality="final",
    )

    record_dir = get_new_record_dir(before) or get_latest_record_dir()
    bundle = load_record_bundle(record_dir)
    pkg = bundle["note_package"]
    page = (pkg.get("pages") or [{}])[0]

    checks = {}
    checks["run_success"] = result.get("success") is True
    checks["pkg_status_success"] = pkg.get("status") == "success"
    checks["references_empty"] = pkg.get("references") == []
    checks["page_reference_ids_empty"] = page.get("reference_ids") == []
    checks["page_used_reference_false"] = page.get("used_reference") is False
    checks["page_generation_mode_txt2img"] = page.get("generation", {}).get("mode") == "text_to_image"

    image_path = page.get("image", {}).get("path")
    checks["page_image_exists"] = assert_file_exists(image_path)
    checks["generated_assets_nonempty"] = len(list(bundle["generated_dir"].glob("*"))) > 0
    checks["references_assets_empty"] = len(list(bundle["references_dir"].glob("*"))) == 0

    display = pkg.get("display", {})
    checks["display_cover_matches_page_image"] = display.get("cover_image_path") == image_path
    checks["display_reference_thumb_empty"] = display.get("reference_thumbnail_path") in (None, "")

    checks.update(check_common_record_integrity(bundle))

    history_exists, rows, matches = check_history_index_contains(pkg.get("record_id"))
    checks["history_index_exists"] = history_exists
    checks["history_index_has_record"] = len(matches) >= 1
    if matches:
        checks["history_used_reference_false"] = matches[-1].get("used_reference") is False
    else:
        checks["history_used_reference_false"] = False

    passed = all(checks.values())

    result_data = {
        "passed": passed,
        "record_dir": str(record_dir),
        "checks": checks,
        "result": result,
    }
    REPORT["results"]["B_no_ref_txt2img"] = result_data
    print(json.dumps(result_data, ensure_ascii=False, indent=2))
    return result_data


def test_C_invalid_case_fallback():
    print_title("【测试 C】无效 case_id fallback 文生图")

    before = snapshot_record_names()

    result = run(
        user_input=TEST_BRIEF,
        use_reference=True,
        case_id=INVALID_CASE_ID,
        task="poster",
        direction="balanced",
        aspect="3:4",
        quality="final",
    )

    record_dir = get_new_record_dir(before) or get_latest_record_dir()
    bundle = load_record_bundle(record_dir)
    pkg = bundle["note_package"]
    page = (pkg.get("pages") or [{}])[0]

    checks = {}
    checks["references_empty"] = pkg.get("references") == []
    checks["page_reference_ids_empty"] = page.get("reference_ids") == []
    checks["page_used_reference_false"] = page.get("used_reference") is False
    checks["page_generation_mode_txt2img"] = page.get("generation", {}).get("mode") == "text_to_image"

    if result.get("success"):
        checks["fallback_success"] = True
        checks["pkg_status_success"] = pkg.get("status") == "success"
        image_path = page.get("image", {}).get("path")
        checks["page_image_exists"] = assert_file_exists(image_path)
    else:
        checks["fallback_success"] = False
        checks["pkg_status_failed"] = pkg.get("status") == "failed"
        checks["page_image_exists"] = True

    checks.update(check_common_record_integrity(bundle))

    passed = (
        checks["references_empty"]
        and checks["page_reference_ids_empty"]
        and checks["page_used_reference_false"]
        and checks["page_generation_mode_txt2img"]
    )

    result_data = {
        "passed": passed,
        "record_dir": str(record_dir),
        "checks": checks,
        "result": result,
    }
    REPORT["results"]["C_invalid_case_fallback"] = result_data
    print(json.dumps(result_data, ensure_ascii=False, indent=2))
    return result_data


def test_D_archive_consistency():
    print_title("【测试 D】归档一致性检查（最新记录）")

    record_dir = get_latest_record_dir()
    if not record_dir:
        result_data = {"passed": False, "error": "没有找到任何 record_dir"}
        REPORT["results"]["D_archive_consistency"] = result_data
        print(json.dumps(result_data, ensure_ascii=False, indent=2))
        return result_data

    bundle = load_record_bundle(record_dir)
    pkg = bundle["note_package"]
    arc = bundle["archive"]
    page = (pkg.get("pages") or [{}])[0]

    checks = {}
    checks["record_id_same"] = pkg.get("record_id") == record_dir.name
    checks["archive_generation_status_same"] = arc.get("generation", {}).get("status") == pkg.get("status")
    checks["archive_prompt_matches_pkg_page_prompt"] = (
        arc.get("generation", {}).get("final_prompt") == page.get("prompt", {}).get("final_prompt")
    )

    pkg_mode = page.get("generation", {}).get("mode")
    arc_used_ref = arc.get("generation", {}).get("used_reference")

    if pkg_mode == "image_to_image":
        checks["archive_used_reference_true_for_img2img"] = arc_used_ref is True
    else:
        checks["archive_used_reference_false_for_txt2img"] = arc_used_ref is False

    if pkg.get("status") == "success":
        checks["pkg_cover_exists"] = assert_file_exists(pkg.get("display", {}).get("cover_image_path"))
    else:
        checks["pkg_cover_exists"] = True

    passed = all(checks.values())

    result_data = {
        "passed": passed,
        "record_dir": str(record_dir),
        "checks": checks,
    }
    REPORT["results"]["D_archive_consistency"] = result_data
    print(json.dumps(result_data, ensure_ascii=False, indent=2))
    return result_data


def test_E_path_audit():
    print_title("【测试 E】路径审计")

    audit = check_forbidden_paths()
    REPORT["results"]["E_path_audit"] = audit
    print(json.dumps(audit, ensure_ascii=False, indent=2))
    return audit


def test_F_record_id_collision():
    print_title("【测试 F】record_id 唯一性检查")

    ids = [generate_record_id() for _ in range(20)]
    unique_count = len(set(ids))

    result_data = {
        "passed": unique_count == len(ids),
        "total": len(ids),
        "unique": unique_count,
        "sample_ids": ids[:5],
    }
    REPORT["results"]["F_record_id_collision"] = result_data
    print(json.dumps(result_data, ensure_ascii=False, indent=2))
    return result_data


def test_G_optional_failure_archive():
    print_title("【测试 G】可选：失败归档测试")

    if os.getenv("PHASE05_FORCE_FAILURE") != "1":
        result_data = {
            "passed": True,
            "skipped": True,
            "reason": "未设置 PHASE05_FORCE_FAILURE=1，跳过真实失败测试"
        }
        REPORT["results"]["G_optional_failure_archive"] = result_data
        print(json.dumps(result_data, ensure_ascii=False, indent=2))
        return result_data

    result_data = {
        "passed": False,
        "skipped": True,
        "reason": "需要按项目实际失败注入方式补充"
    }
    REPORT["results"]["G_optional_failure_archive"] = result_data
    print(json.dumps(result_data, ensure_ascii=False, indent=2))
    return result_data


def main():
    print_title("Phase 0.5 严格版端到端验收测试")
    print(f"项目根目录：{PROJECT_ROOT}")
    print(f"输出目录：{OUTPUT_DIR}")
    print(f"开始时间：{datetime.now().isoformat()}")

    test_A_valid_case_img2img()
    test_B_no_ref_txt2img()
    test_C_invalid_case_fallback()
    test_D_archive_consistency()
    test_E_path_audit()
    test_F_record_id_collision()
    test_G_optional_failure_archive()

    print_title("测试汇总")

    passed_count = 0
    total_count = 0

    for name, data in REPORT["results"].items():
        total_count += 1
        passed = bool(data.get("passed"))
        if passed:
            passed_count += 1
        print(f"{'✅' if passed else '❌'} {name}")

    REPORT["passed_count"] = passed_count
    REPORT["total_count"] = total_count
    REPORT["all_passed"] = passed_count == total_count

    report_path = OUTPUT_DIR / "test_phase05_strict_report.json"
    report_path.write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n通过：{passed_count}/{total_count}")
    print(f"报告路径：{report_path}")
    print(f"结束时间：{datetime.now().isoformat()}")

    return 0 if REPORT["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
