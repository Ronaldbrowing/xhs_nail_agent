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
    - If resolved path doesn't exist, try cleaning newline characters from directory names.
    """
    p = Path(path)
    if p.is_absolute():
        resolved = p.resolve()
    else:
        resolved = (PROJECT_ROOT / p).resolve()

    if resolved.exists():
        return resolved

    # If path doesn't exist, try to find the actual directory with newline in the name
    if not p.is_absolute():
        parts = list(Path(path).parts)  # e.g. ['case_library', 'poster', 'case_001_xxx.\n', 'image.png']
        if len(parts) >= 3:
            # Search for directories that match the cleaned name
            search_root = PROJECT_ROOT
            for i, part in enumerate(parts[:-1]):
                cleaned_part = part.replace("\\n", "").replace("\n", "").strip()
                if not cleaned_part:
                    continue
                # Look for matching directory
                if i == 0:
                    candidates = [search_root / d for d in search_root.iterdir() if d.is_dir() and d.name.replace("\n", "").strip() == cleaned_part]
                else:
                    parent = search_root
                    candidates = [parent / d for d in parent.iterdir() if d.is_dir() and d.name.replace("\n", "").strip() == cleaned_part]
                if candidates:
                    search_root = candidates[0]
                else:
                    break
            else:
                # Found all cleaned parts, try the last part
                img_path = search_root / parts[-1]
                if img_path.exists():
                    return img_path

            # Alternative: try with original last dir part that might have newline
            if len(parts) >= 3:
                base_dir = parts[-2]  # e.g. 'case_001_xxx.\n'
                cleaned_base = base_dir.replace("\\n", "").replace("\n", "").strip()
                parent_path = PROJECT_ROOT
                for part in parts[:-2]:
                    parent_path = parent_path / part
                if parent_path.exists():
                    for d in parent_path.iterdir():
                        cleaned = d.name.replace("\n", "").replace("\\n", "").strip()
                        if cleaned == cleaned_base and d.is_dir():
                            img = d / parts[-1]
                            if img.exists():
                                return img

    return resolved
