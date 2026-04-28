from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"
CASE_LIBRARY_DIR = PROJECT_ROOT / "case_library"


def ensure_project_dirs() -> None:
    """Create output/ and case_library/ directories if they don't exist."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CASE_LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    for task in ["poster", "product", "ppt", "infographic", "teaching"]:
        (CASE_LIBRARY_DIR / task).mkdir(exist_ok=True)


def to_project_relative(path) -> str:
    """
    Return the path relative to PROJECT_ROOT as a string.
    If path is not under PROJECT_ROOT, return the original string or a readable representation.
    """
    try:
        p = Path(path).resolve()
        if p.is_relative_to(PROJECT_ROOT):
            return str(p.relative_to(PROJECT_ROOT))
        return str(p)
    except Exception:
        return str(path)


def resolve_project_path(path) -> Path:
    """
    Return a resolved absolute Path.
    - If input is an absolute path, return it resolved.
    - If input is a relative path, resolve it relative to PROJECT_ROOT.
    """
    p = Path(path)
    if p.is_absolute():
        return p.resolve()
    return (PROJECT_ROOT / p).resolve()
