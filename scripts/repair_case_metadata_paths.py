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

        # Skip .venv, .git, backup dirs
        if any(part.startswith('.') for part in case_dir.parts):
            continue

        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        stored_path = meta.get("image_path", "")

        # Resolve stored_path: if it's relative, resolve from PROJECT_ROOT
        if stored_path:
            stored_path_obj = Path(stored_path)
            if stored_path_obj.is_absolute():
                stored_resolved = stored_path_obj
            else:
                stored_resolved = PROJECT_ROOT / stored_path_obj
        else:
            stored_resolved = None

        # Try to find a valid local image
        local_image = None
        for ext in IMAGE_EXTS:
            img = case_dir / f"image{ext}"
            if img.exists():
                local_image = img
                break

        # If no local image, try to copy from stored path (if it's absolute and exists)
        if local_image is None and stored_resolved and stored_resolved.exists():
            ext = stored_resolved.suffix or ".png"
            new_img_path = case_dir / f"image{ext}"
            shutil.copy2(stored_resolved, new_img_path)
            print(f"  [COPY] {stored_resolved} -> {new_img_path.relative_to(PROJECT_ROOT)}")
            local_image = new_img_path

        if local_image is None:
            print(f"  [SKIP] {meta_file.relative_to(CASE_LIBRARY_DIR)}: no local image found")
            skipped_count += 1
            continue

        # Check if stored_path already points to this local_image (relative path already correct)
        if stored_resolved and stored_resolved.exists() and stored_resolved.resolve() == local_image.resolve():
            # Already correct
            skipped_count += 1
            continue

        old_path = stored_path

        # Backup original
        bak_path = meta_file.with_suffix(meta_file.suffix + ".bak.path")
        shutil.copy2(meta_file, bak_path)
        print(f"  [BACKUP] {meta_file.relative_to(CASE_LIBRARY_DIR)} -> {bak_path.name}")

        # Update to relative path pointing to local_image
        relative_path = to_project_relative(local_image)
        meta["image_path"] = relative_path

        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        print(f"  [REPAIR] {meta_file.relative_to(CASE_LIBRARY_DIR)}: '{old_path}' -> '{relative_path}'")
        repaired_count += 1

    print(f"\nDone. Repaired: {repaired_count}, Skipped (already valid): {skipped_count}")
    return repaired_count


if __name__ == "__main__":
    print("Repairing case_library metadata paths...")
    print(f"Case library: {CASE_LIBRARY_DIR}\n")
    repair_metadata_paths()
