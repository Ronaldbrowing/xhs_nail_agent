#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from project_paths import resolve_project_path
from verticals.nail.note_workflow import NailNoteWorkflow
from verticals.nail.schemas import UserInput


def _guard_real_api() -> int:
    if os.environ.get("RUN_REAL_IMAGE_TESTS") == "1":
        return 0
    print("SKIP: set RUN_REAL_IMAGE_TESTS=1 to call the real image API")
    return 1


def main() -> int:
    if _guard_real_api():
        return 0

    parser = argparse.ArgumentParser(description="Run real nail note image integration without references.")
    parser.add_argument("--max-workers", type=int, default=1)
    args = parser.parse_args()

    print("reference_source=none")
    print("reference_image_path=None")
    print("case_id=None")

    workflow = NailNoteWorkflow()
    user_input = UserInput(
        brief="夏日蓝色猫眼短甲，适合黄皮，显白清透，小红书种草图文",
        style_id="single_seed_summer_cat_eye_short",
        skin_tone="黄皮",
        nail_length="短甲",
        nail_shape="短方圆",
        note_goal="seed",
        page_count=6,
        generate_images=True,
        generate_copy=True,
        generate_tags=True,
        allow_text_on_image=False,
        quality="draft",
        aspect="3:4",
        direction="balanced",
        reference_image_path=None,
        case_id=None,
        max_workers=args.max_workers,
    )

    package = workflow.generate_note(user_input)

    print("\n=== REAL IMAGE INTEGRATION RESULT ===")
    print("note_id:", package.note_id)
    print("success:", package.success)
    print("partial_failure:", package.partial_failure)
    print("output_dir:", package.output_dir)
    print("package_path:", package.package_path)
    print("qa_score:", package.diagnostics.get("qa_score"))
    print("reference:", json.dumps(package.diagnostics.get("reference", {}), ensure_ascii=False))

    for page in package.pages:
        image_exists = False
        if page.image_path:
            image_exists = resolve_project_path(page.image_path).exists()
        print(
            "page_{page_no}: role={role} status={status} image_path={image_path} exists={exists} issues={issues}".format(
                page_no=page.page_no,
                role=page.role,
                status=page.status,
                image_path=page.image_path,
                exists=image_exists,
                issues=page.issues,
            )
        )

    if package.package_path:
        pkg_path = resolve_project_path(package.package_path)
        print("package_exists:", pkg_path.exists())
        if pkg_path.exists():
            data = json.loads(pkg_path.read_text(encoding="utf-8"))
            print("saved_success:", data.get("success"))
            print("saved_partial_failure:", data.get("partial_failure"))
            print("saved_qa_score:", data.get("diagnostics", {}).get("qa_score"))

    failed_pages = [page for page in package.pages if page.status == "failed"]
    missing_images = [
        page for page in package.pages
        if page.status == "generated" and (not page.image_path or not resolve_project_path(page.image_path).exists())
    ]

    if not package.package_path or not resolve_project_path(package.package_path).exists():
        raise SystemExit("FAIL: note_package.json not found")
    if missing_images:
        raise SystemExit("FAIL: generated pages with missing images: {pages}".format(pages=[page.page_no for page in missing_images]))
    if package.success:
        print("PASS: real image integration succeeded")
        return 0
    if package.partial_failure and not failed_pages[:1]:
        print("WARN: partial failure, but cover may have succeeded")
        return 0
    raise SystemExit("FAIL: workflow did not succeed")


if __name__ == "__main__":
    raise SystemExit(main())
