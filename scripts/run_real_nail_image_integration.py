import json
import sys
from pathlib import Path

# 确保项目根目录在 Python path 中
_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from project_paths import resolve_project_path
from verticals.nail.note_workflow import NailNoteWorkflow
from verticals.nail.schemas import UserInput


def main():
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
    )

    package = workflow.generate_note(user_input)

    print("\n=== REAL IMAGE INTEGRATION RESULT ===")
    print("note_id:", package.note_id)
    print("success:", package.success)
    print("partial_failure:", package.partial_failure)
    print("output_dir:", package.output_dir)
    print("package_path:", package.package_path)
    print("qa_score:", package.diagnostics.get("qa_score"))
    print("qa_error:", package.diagnostics.get("qa_error"))

    for page in package.pages:
        image_exists = False
        if page.image_path:
            image_exists = resolve_project_path(page.image_path).exists()

        print(
            f"page_{page.page_no}: "
            f"role={page.role} "
            f"status={page.status} "
            f"image_path={page.image_path} "
            f"exists={image_exists} "
            f"issues={page.issues}"
        )

    if package.package_path:
        pkg_path = resolve_project_path(package.package_path)
        print("package_exists:", pkg_path.exists())

        if pkg_path.exists():
            data = json.loads(pkg_path.read_text(encoding="utf-8"))
            print("saved_success:", data.get("success"))
            print("saved_partial_failure:", data.get("partial_failure"))
            print("saved_qa_score:", data.get("diagnostics", {}).get("qa_score"))

    failed_pages = [p for p in package.pages if p.status == "failed"]
    missing_images = [
        p for p in package.pages
        if p.status == "generated" and (not p.image_path or not resolve_project_path(p.image_path).exists())
    ]

    if not package.package_path or not resolve_project_path(package.package_path).exists():
        raise SystemExit("FAIL: note_package.json not found")

    if missing_images:
        raise SystemExit(f"FAIL: generated pages with missing images: {[p.page_no for p in missing_images]}")

    if package.success:
        print("PASS: real image integration succeeded")
    elif package.partial_failure and not failed_pages[:1]:
        print("WARN: partial failure, but cover may have succeeded")
    else:
        raise SystemExit("FAIL: workflow did not succeed")


if __name__ == "__main__":
    main()

