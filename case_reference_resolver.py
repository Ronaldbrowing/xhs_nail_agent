from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parent
CASE_LIBRARY_ROOT = PROJECT_ROOT / "case_library"


def resolve_case_image_path(
    case_id: str,
    task: str = "poster",
    filename: str = "image.png",
) -> str:
    """
    Resolve a case_id like 'case_004' to its reference image path.

    Example:
        case_library/poster/case_004_xxx/image.png
    """
    case_dir_root = CASE_LIBRARY_ROOT / task

    if not case_dir_root.exists():
        raise FileNotFoundError(f"Case task directory not found: {case_dir_root}")

    candidates = sorted(case_dir_root.glob(f"{case_id}*/{filename}"))

    if not candidates:
        raise FileNotFoundError(
            f"No reference image found for case_id={case_id!r}, task={task!r}, filename={filename!r}"
        )

    if len(candidates) > 1:
        print(f"[WARN] Multiple reference images matched case_id={case_id!r}; using first:")
        for item in candidates:
            print(f"  - {item}")

    return str(candidates[0])


def try_resolve_case_image_path(
    case_id: Optional[str],
    task: str = "poster",
    filename: str = "image.png",
) -> Optional[str]:
    if not case_id:
        return None

    try:
        return resolve_case_image_path(case_id=case_id, task=task, filename=filename)
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 case_reference_resolver.py <case_id> [task]")
        raise SystemExit(1)

    case_id = sys.argv[1]
    task = sys.argv[2] if len(sys.argv) >= 3 else "poster"

    path = resolve_case_image_path(case_id=case_id, task=task)
    print(path)
