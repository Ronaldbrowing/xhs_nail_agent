"""
record_manager.py — Record directory and package archival.
Creates record_dir/ and writes note_package.json / archive.json
with full lineage, diagnostics, and project-relative paths.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Any

from project_paths import PROJECT_ROOT, OUTPUT_DIR, to_project_relative


def generate_record_id(prefix: str = "image") -> str:
    """Generate record_id = prefix_YYYYMMDD_HHMMSS_{8-char uuid4}

    Uses uuid4 for collision resistance —同一秒内连续生成也不会重复。
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_part = uuid.uuid4().hex[:8]
    return f"{prefix}_{ts}_{unique_part}"


def create_record_dir(record_id: str, output_dir: Path = None) -> Path:
    """Create record_dir = output_dir/records/{record_id}/"""
    if output_dir is None:
        output_dir = OUTPUT_DIR
    records_dir = output_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    record_dir = records_dir / record_id
    record_dir.mkdir(parents=True, exist_ok=True)
    return record_dir


def write_note_package(package: dict, record_dir: Path) -> str:
    """
    Write note_package.json into record_dir.
    Returns the project-relative path.
    """
    pkg_path = record_dir / "note_package.json"
    with open(pkg_path, "w", encoding="utf-8") as f:
        json.dump(package, f, indent=2, ensure_ascii=False)
    return to_project_relative(pkg_path)


def write_archive(archive: dict, record_dir: Path) -> str:
    """
    Write archive.json into record_dir.
    Returns the project-relative path.
    """
    arch_path = record_dir / "archive.json"
    with open(arch_path, "w", encoding="utf-8") as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)
    return to_project_relative(arch_path)


def build_record_archive(
    record_id: str,
    user_input: str,
    prompt_data: dict,
    style_data: dict,
    generation: dict,
    qa: dict,
    workflow_diagnostics: dict,
    model_usage: dict,
    dna_summary: str,
    references: list,
    pages: list,
    input_fields: dict,
) -> dict:
    """
    Build the full archive dict per PRD requirement #23.
    archive.json must contain record_id, input, references, pages, quality, files.
    """
    normalized_gen = dict(generation)
    if generation.get("filepath"):
        normalized_gen["filepath"] = to_project_relative(generation["filepath"])

    return {
        "record_id": record_id,
        "timestamp": datetime.now().isoformat(),
        "input": input_fields,
        "references": references,
        "pages": pages,
        "quality": qa,
        "files": {
            "generation_filepath": normalized_gen.get("filepath"),
        },
        "prompt_analysis": prompt_data,
        "style_params": style_data,
        "workflow_diagnostics": workflow_diagnostics,
        "model_usage": model_usage,
        "generation": normalized_gen,
        "dna_summary": dna_summary,
    }