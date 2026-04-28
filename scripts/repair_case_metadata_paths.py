#!/usr/bin/env python3
"""
Repair case_library metadata.json files that have old absolute paths.

For each case_library/**/metadata.json:
- If image_path in metadata points to a non-existent location but image exists in same dir, fix image_path
- If image_path points to an OLD path (multi-agent-image) and that old path has the image,
  copy the image to the new case_library dir and update image_path to relative path
- Backup original to metadata.json.bak.path before modifying
"""

import json
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from project_paths import CASE_LIBRARY_DIR, to_project_relative, PROJECT_ROOT


def repair_metadata_paths():
    repaired_count = 0
    skipped_count = 0

    IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".webp"]

    for meta_file in CASE_LIBRARY_DIR.rglob("metadata.json"):
        case_dir = meta_file.parent

        # Skip .venv, .git, backup dirs (only skip if dir name itself starts with .)
        if case_dir.name.startswith('.'):
            continue

        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        stored_path = meta.get("image_path", "")
        original_stored_path = stored_path

        # Handle corrupted paths with actual newline characters or literal \n
        if stored_path and ("\n" in stored_path or "\\n" in stored_path):
            cleaned_parts = [p.strip() for p in stored_path.replace("\\n", "\n").split("\n")]
            stored_path = "".join(parts for parts in cleaned_parts if parts)

        # Resolve stored_path for existence check only
        stored_resolved = None
        if stored_path:
            stored_path_obj = Path(stored_path)
            if stored_path_obj.is_absolute():
                stored_resolved = stored_path_obj
            else:
                stored_resolved = PROJECT_ROOT / stored_path_obj

        # Find valid local image (source of truth)
        local_image = None
        for ext in IMAGE_EXTS:
            img = case_dir / f"image{ext}"
            if img.exists():
                local_image = img
                break

        if local_image is None:
            print(f"  [SKIP] {meta_file.relative_to(CASE_LIBRARY_DIR)}: no local image found")
            skipped_count += 1
            continue

        # Get the correct relative path from the actual local image
        # Normalize path to remove any newline characters
        correct_relative = to_project_relative(local_image)
        if "\n" in correct_relative or "\\n" in correct_relative:
            # Directory name itself has newline - clean it up
            # Use just the directory basename and image filename
            cleaned_dir_name = case_dir.name.replace("\n", "").replace("\\n", "").strip()
            ext = local_image.suffix or ".png"
            correct_relative = f"case_library/{case_dir.parent.name}/{cleaned_dir_name}/image{ext}"

        # Clean stored_path for comparison
        cleaned_stored_path = stored_path
        if "\n" in cleaned_stored_path or "\\n" in cleaned_stored_path:
            cleaned_parts = [p.strip() for p in cleaned_stored_path.replace("\\n", "\n").split("\n")]
            cleaned_stored_path = "".join(parts for parts in cleaned_parts if parts)

        # Verify the stored path actually resolves to an existing file
        # If path doesn't exist (e.g., due to newline in dir name), check if local image exists
        stored_path_resolves = False
        if cleaned_stored_path:
            check_path = PROJECT_ROOT / cleaned_stored_path if not Path(cleaned_stored_path).is_absolute() else Path(cleaned_stored_path)
            stored_path_resolves = check_path.exists()

        # Check if metadata already has the correct relative path
        # If stored_path is absolute (not relative), it needs repair even if file exists
        # Use local_image existence as the source of truth since it handles newlines via filesystem
        stored_is_relative = stored_path and not Path(stored_path).is_absolute()
        if stored_is_relative and local_image and (cleaned_stored_path == correct_relative or stored_path_resolves):
            skipped_count += 1
            continue

        # Repair needed
        old_path = original_stored_path

        # Backup original
        bak_path = meta_file.with_suffix(meta_file.suffix + ".bak.path")
        shutil.copy2(meta_file, bak_path)
        print(f"  [BACKUP] {meta_file.relative_to(CASE_LIBRARY_DIR)} -> {bak_path.name}")

        # Update to correct relative path
        meta["image_path"] = correct_relative

        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        print(f"  [REPAIR] {meta_file.relative_to(CASE_LIBRARY_DIR)}: '{old_path}' -> '{correct_relative}'")
        repaired_count += 1

    print(f"\nDone. Repaired: {repaired_count}, Skipped (already valid): {skipped_count}")
    return repaired_count


if __name__ == "__main__":
    print("Repairing case_library metadata paths...")
    print(f"Case library: {CASE_LIBRARY_DIR}\n")
    repair_metadata_paths()
