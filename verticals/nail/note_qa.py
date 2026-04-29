"""
笔记QA检查器 - 对整篇 NailNotePackage 做规则检查
"""
from typing import Dict, List

from .note_workflow_schemas import NailNotePackage
from project_paths import resolve_project_path


def _check_generated_page_image(page, page_label: str, issues: List[str], score: float) -> float:
    if not page.image_path:
        issues.append("{label} status=generated 但无 image_path".format(label=page_label))
        return score - 1.0

    try:
        image_path = resolve_project_path(page.image_path)
    except Exception:
        image_path = None

    if image_path is None or not image_path.exists():
        issues.append("{label} image_path 不存在: {path}".format(label=page_label, path=page.image_path))
        return score - 1.0

    return score


def qa_note_package(package: NailNotePackage, generate_images: bool = True) -> Dict:
    issues = []
    warnings = []

    structure_score = 10.0
    content_score = 10.0
    image_score = 10.0
    reference_score = 10.0

    reference_info = package.diagnostics.get("reference", {}) if isinstance(package.diagnostics, dict) else {}
    reference_source_type = reference_info.get("source_type", "none")
    has_reference = bool(reference_info.get("resolved_image_path"))

    if not package.pages:
        issues.append("pages 为空")
        structure_score -= 3.0
    else:
        for i, page in enumerate(package.pages, start=1):
            if not page.role:
                issues.append("page_{idx} 缺少 role".format(idx=i))
                structure_score -= 0.5
            if not page.goal:
                issues.append("page_{idx} 缺少 goal".format(idx=i))
                structure_score -= 0.3
            if not page.visual_brief:
                issues.append("page_{idx} 缺少 visual_brief".format(idx=i))
                structure_score -= 0.3
            if not page.prompt:
                warnings.append("page_{idx} 缺少 prompt".format(idx=i))
                structure_score -= 0.2
            if page.status == "failed":
                issues.append("page_{idx} 生成失败: {issues}".format(idx=i, issues=", ".join(page.issues)))
                image_score -= 1.0

    if package.pages:
        first_role = package.pages[0].role.value if hasattr(package.pages[0].role, "value") else package.pages[0].role
        if first_role != "cover":
            issues.append("第1页角色应该是 cover，实际是 {role}".format(role=first_role))
            structure_score -= 1.0

    if len(package.title_candidates) < 10:
        issues.append("标题候选只有 {count} 个，需要至少10个".format(count=len(package.title_candidates)))
        content_score -= 1.0
    if not package.selected_title:
        issues.append("未选择标题")
        content_score -= 0.8

    if not package.body:
        issues.append("正文为空")
        content_score -= 2.0
    elif len(package.body) < 100:
        issues.append("正文太短，只有 {count} 字".format(count=len(package.body)))
        content_score -= 1.0

    if len(package.tags) < 15:
        issues.append("TAG 只有 {count} 个，需要至少15个".format(count=len(package.tags)))
        content_score -= 1.0
    elif len(package.tags) > 25:
        warnings.append("TAG 有 {count} 个，超过推荐上限25个".format(count=len(package.tags)))
        content_score -= 0.2

    if len(package.comment_hooks) < 3:
        issues.append("评论钩子只有 {count} 个，需要至少3个".format(count=len(package.comment_hooks)))
        content_score -= 1.0

    if package.output_dir and package.output_dir.startswith("/"):
        warnings.append("output_dir 是绝对路径: {path}".format(path=package.output_dir))
    if package.package_path and package.package_path.startswith("/"):
        warnings.append("package_path 是绝对路径: {path}".format(path=package.package_path))

    if not package.package_path:
        issues.append("package_path 为空，package 尚未保存")
        structure_score -= 1.0
    else:
        pkg_path = resolve_project_path(package.package_path)
        if not pkg_path.exists():
            issues.append("note_package.json 不存在: {path}".format(path=package.package_path))
            structure_score -= 1.0

    if not package.archive_path:
        issues.append("archive_path 为空，archive 尚未保存")
        structure_score -= 1.0
    else:
        archive_path = resolve_project_path(package.archive_path)
        if not archive_path.exists():
            issues.append("archive.json 不存在: {path}".format(path=package.archive_path))
            structure_score -= 1.0

    if not package.visual_dna:
        issues.append("visual_dna 为空")
        structure_score -= 1.0

    if generate_images and package.pages:
        for index, page in enumerate(package.pages, start=1):
            if page.status == "generated":
                image_score = _check_generated_page_image(page, "第{idx}页".format(idx=index), issues, image_score)
            elif index == 1 and page.status == "failed":
                issues.append("封面页生成失败")
                image_score -= 2.0

    if has_reference:
        if reference_source_type == "case_id" and not reference_info.get("case_id"):
            issues.append("reference.source_type=case_id 但 diagnostics.reference.case_id 为空")
            reference_score -= 1.0
        if reference_source_type == "local_path" and not reference_info.get("resolved_image_path"):
            issues.append("reference.source_type=local_path 但 diagnostics.reference.resolved_image_path 为空")
            reference_score -= 1.0
        for page in package.pages:
            if page.status == "generated" and not page.used_reference:
                issues.append("reference 已启用，但 page_{page_no} 未标记 used_reference=True".format(page_no=page.page_no))
                reference_score -= 0.5
    elif reference_source_type != "none":
        warnings.append("reference source 已声明为 {source}，但无 resolved_image_path".format(source=reference_source_type))
        reference_score -= 0.5

    structure_score = max(0.0, min(10.0, structure_score))
    content_score = max(0.0, min(10.0, content_score))
    image_score = max(0.0, min(10.0, image_score))
    reference_score = max(0.0, min(10.0, reference_score))
    overall_score = round((structure_score + content_score + image_score + reference_score) / 4.0, 1)
    passed = len(issues) == 0 and overall_score >= 8.0

    return {
        "passed": passed,
        "score": overall_score,
        "structure_score": round(structure_score, 1),
        "content_score": round(content_score, 1),
        "image_score": round(image_score, 1),
        "reference_score": round(reference_score, 1),
        "issues": issues,
        "warnings": warnings,
    }
