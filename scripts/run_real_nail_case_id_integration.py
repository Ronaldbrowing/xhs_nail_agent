#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from verticals.nail.note_workflow import NailNoteWorkflow
from verticals.nail.note_workflow_schemas import NailNoteUserInput


def _guard_real_api() -> int:
    if os.environ.get("RUN_REAL_IMAGE_TESTS") == "1":
        return 0
    print("SKIP: set RUN_REAL_IMAGE_TESTS=1 to call the real image API")
    return 1


def main() -> int:
    if _guard_real_api():
        return 0

    parser = argparse.ArgumentParser(description="Run real nail note image integration with a case_id reference.")
    parser.add_argument("--case-id", default=None)
    parser.add_argument("--max-workers", type=int, default=1)
    args = parser.parse_args()

    case_id = args.case_id or "case_038"
    print("reference_source=case_id")
    print("case_id={case_id}".format(case_id=case_id))
    print("reference_image_path=None")

    user_input = NailNoteUserInput(
        brief="夏日蓝色猫眼短甲，清透显白，参考历史案例风格",
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
        aspect="3:4",
        direction="balanced",
        reference_image_path=None,
        case_id=case_id,
        max_workers=args.max_workers,
    )

    workflow = NailNoteWorkflow()
    package = workflow.generate_note(user_input)
    print("qa_score={score}".format(score=package.diagnostics.get("qa_score")))
    return 0 if package.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
