"""
笔记QA检查器 - 对整篇 NailNotePackage 做规则检查
"""
from typing import Dict
from .note_workflow_schemas import NailNotePackage
from project_paths import resolve_project_path


def _check_generated_page_image(page, page_label: str, issues: list, score: float) -> float:
    """Validate image_path for any generated page."""
    if not page.image_path:
        issues.append(f"{page_label} status=generated 但无 image_path")
        return score - 1.0

    try:
        image_path = resolve_project_path(page.image_path)
    except Exception:
        image_path = None

    if image_path is None or not image_path.exists():
        issues.append(f"{page_label} image_path 不存在: {page.image_path}")
        return score - 1.0

    return score


def qa_note_package(package: NailNotePackage, generate_images: bool = True) -> Dict:
    """
    对 NailNotePackage 做规则 QA 检查。

    Args:
        package: NailNotePackage
        generate_images: 是否生成了图片（影响图片路径检查）

    Returns:
        dict with keys: passed (bool), score (float), issues (list[str])
    """
    issues = []
    score = 10.0

    # 1. 检查 pages 基本信息
    if not package.pages:
        issues.append("pages 为空")
        score -= 3
    else:
        for i, page in enumerate(package.pages):
            if not page.role:
                issues.append(f"page_{i+1} 缺少 role")
                score -= 0.5
            if not page.goal:
                issues.append(f"page_{i+1} 缺少 goal")
                score -= 0.3
            if not page.visual_brief:
                issues.append(f"page_{i+1} 缺少 visual_brief")
                score -= 0.3
            if not page.prompt:
                issues.append(f"page_{i+1} 缺少 prompt")
                score -= 0.5
            if page.status == "failed":
                issues.append(f"page_{i+1} 生成失败: {', '.join(page.issues)}")
                score -= 1.0

    # 2. 检查封面页角色
    if package.pages:
        first_role = package.pages[0].role
        if hasattr(first_role, 'value'):
            first_role = first_role.value
        if first_role != "cover":
            issues.append(f"第1页角色应该是 cover，实际是 {first_role}")
            score -= 1.0

    # 3. 检查标题
    if len(package.title_candidates) < 10:
        issues.append(f"标题候选只有 {len(package.title_candidates)} 个，需要至少10个")
        score -= 1.0
    if not package.selected_title:
        issues.append("未选择标题")
        score -= 0.5

    # 4. 检查正文
    if not package.body:
        issues.append("正文为空")
        score -= 2.0
    elif len(package.body) < 100:
        issues.append(f"正文太短，只有 {len(package.body)} 字")
        score -= 1.0

    # 5. 检查 TAG
    if len(package.tags) < 15:
        issues.append(f"TAG 只有 {len(package.tags)} 个，需要至少15个")
        score -= 1.0
    elif len(package.tags) > 25:
        issues.append(f"TAG 有 {len(package.tags)} 个，最多25个")
        score -= 0.3

    # 6. 检查评论钩子
    if len(package.comment_hooks) < 3:
        issues.append(f"评论钩子只有 {len(package.comment_hooks)} 个，需要至少3个")
        score -= 1.0

    # 7. 检查路径格式（相对路径）
    if package.output_dir and package.output_dir.startswith("/"):
        issues.append(f"output_dir 是绝对路径: {package.output_dir}")
        score -= 0.5
    if package.package_path and package.package_path.startswith("/"):
        issues.append(f"package_path 是绝对路径: {package.package_path}")
        score -= 0.5

    # 8. 图片相关检查（仅 generate_images=True 时）
    if generate_images and package.pages:
        cover_page = package.pages[0]
        cover_role = cover_page.role
        if hasattr(cover_role, 'value'):
            cover_role = cover_role.value
        if cover_role != "cover":
            issues.append(f"第1页角色应该是 cover，实际是 {cover_role}")
            score -= 1.0
        # 封面页状态检查
        if cover_page.status == "generated":
            prev_score = score
            score = _check_generated_page_image(cover_page, "封面页", issues, score)
            if score < prev_score:
                score -= 1.0
        elif cover_page.status == "failed":
            issues.append("封面页生成失败")
            score -= 2.0

        # 检查内页图片路径
        for i, page in enumerate(package.pages[1:], start=2):
            if page.status == "generated":
                score = _check_generated_page_image(page, f"第{i}页", issues, score)

    # 9. package 保存检查（generate_images=True 时才检查）
    if generate_images:
        if not package.package_path:
            issues.append("package_path 为空，package 尚未保存")
            score -= 1.0
        else:
            try:
                pkg_p = resolve_project_path(package.package_path)
                if not pkg_p.exists():
                    issues.append(f"note_package.json 不存在: {package.package_path}")
                    score -= 1.0
            except Exception:
                pass

    # 10. 检查视觉DNA
    if not package.visual_dna:
        issues.append("visual_dna 为空")
        score -= 1.0

    # 综合评分
    score = max(0.0, min(10.0, score))
    passed = len(issues) == 0 and score >= 8.0

    return {
        "passed": passed,
        "score": round(score, 1),
        "issues": issues,
    }
