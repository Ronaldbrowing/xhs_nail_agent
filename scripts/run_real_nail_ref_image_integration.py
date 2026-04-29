#!/usr/bin/env python3
"""
第二步集成测试：reference_image_path 参考图链路
验证传入参考图后，图片生成链路是否正常工作。

用法：
  # 自动使用第一步输出的封面图作为参考图
  python3 scripts/run_real_nail_ref_image_integration.py

  # 指定参考图路径
  python3 scripts/run_real_nail_ref_image_integration.py /path/to/ref.png
"""
import os
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from verticals.nail.note_workflow_schemas import NailNoteUserInput
from verticals.nail.note_workflow import NailNoteWorkflow


def find_ref_image(user_path: Optional[str] = None) -> Path:
    """找到参考图：优先用户指定 → 回退到第一步输出"""
    if user_path:
        p = Path(user_path)
        if p.exists():
            return p
        print(f"❌ 指定参考图不存在: {user_path}")
        sys.exit(1)

    # 自动找第一步输出目录中最新的封面图
    output_dir = PROJECT_ROOT / "output"
    nail_dirs = sorted(
        output_dir.glob("nail_*_single_seed_summer_cat_eye_short"),
        key=os.path.getmtime, reverse=True,
    )
    for d in nail_dirs:
        cover = d / "page_01_cover.png"
        if cover.exists():
            return cover

    print("❌ 未找到第一步输出，请手动指定参考图路径")
    sys.exit(1)


def main():
    ref_path = sys.argv[1] if len(sys.argv) > 1 else None
    ref_image = find_ref_image(ref_path)

    print("=" * 70)
    print("💅 Step 2: reference_image_path 参考图链路集成测试")
    print("=" * 70)
    print(f"📷 参考图: {ref_image}")
    print()

    user_input = NailNoteUserInput(
        brief="夏日蓝色猫眼短甲，清透显白，参考图中同款风格",
        style_id="single_seed_summer_cat_eye_short",
        skin_tone="黄皮",
        nail_length="短甲",
        nail_shape="短方圆",
        note_goal="seed",
        page_count=6,
        generate_images=True,
        generate_copy=True,
        generate_tags=True,
        quality="draft",
        case_id="case_038",          # ← 替换 reference_image_path
        #reference_image_path=str(ref_image),
    )

    workflow = NailNoteWorkflow()
    package = workflow.generate_note(user_input)

    # ── 验收检查 ──
    print()
    print("=" * 70)
    print("📋 第二步验收检查")
    print("=" * 70)

    checks = {
        "success=True": package.success,
        "partial_failure=False": not package.partial_failure,
    }

    generated = sum(1 for p in package.pages if p.status == "generated")
    checks[f"pages generated: {generated}/6"] = generated == 6

    ref_used = sum(1 for p in package.pages if p.used_reference)
    checks[f"used_reference=True: {ref_used}/6"] = ref_used == 6

    all_exist = True
    for p in package.pages:
        if p.image_path:
            if not (PROJECT_ROOT / p.image_path).exists():
                all_exist = False
    checks["all image_path exist"] = all_exist

    qa = package.diagnostics.get("qa_score", 0)
    checks[f"qa_score={qa}"] = isinstance(qa, (int, float)) and qa >= 7

    pkg_ok = bool(package.package_path and Path(package.package_path).exists())
    checks["note_package.json exists"] = pkg_ok

    all_pass = True
    for label, result in checks.items():
        mark = "✅" if result else "❌"
        if not result:
            all_pass = False
        print(f"  {mark} {label}")

    print()
    print("🎉 第二步验收通过！" if all_pass else "⚠️ 第二步验收未通过")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
