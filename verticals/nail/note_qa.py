"""
笔记QA检查器 - 对整篇 NailNotePackage 做规则检查
"""
from typing import Dict, List
from .note_workflow_schemas import NailNotePackage, NotePageSpec


def qa_note_package(package: NailNotePackage) -> Dict:
    """
    对 NailNotePackage 做规则 QA 检查。
    
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
    
    # 2. 检查封面页
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
    
    # 7. 检查路径
    if package.output_dir and package.output_dir.startswith("/"):
        issues.append(f"output_dir 是绝对路径: {package.output_dir}")
        score -= 0.5
    if package.package_path and package.package_path.startswith("/"):
        issues.append(f"package_path 是绝对路径: {package.package_path}")
        score -= 0.5

    # 8. 检查封面页
    if package.pages:
        cover_page = package.pages[0]
        cover_role = cover_page.role
        if hasattr(cover_role, 'value'):
            cover_role = cover_role.value
        if cover_role != "cover":
            issues.append(f"第1页角色应该是 cover，实际是 {cover_role}")
            score -= 1.0
        # 封面页状态检查（如果生成了图片）
        if cover_page.status == "generated":
            if not cover_page.image_path:
                issues.append("封面页 status=generated 但无 image_path")
                score -= 2.0
            else:
                # 检查图片路径是否存在
                try:
                    from pathlib import Path
                    img_p = Path(cover_page.image_path)
                    if not img_p.is_absolute():
                        from project_paths import PROJECT_ROOT
                        img_p = PROJECT_ROOT / img_p
                    if not img_p.exists():
                        issues.append(f"封面图片路径不存在: {cover_page.image_path}")
                        score -= 2.0
                except Exception:
                    pass
        elif cover_page.status == "failed":
            issues.append("封面页生成失败")
            score -= 2.0

    # 9. 检查内页图片路径（status=generated 的页面必须有 image_path）
    for i, page in enumerate(package.pages[1:], start=2):
        if page.status == "generated" and not page.image_path:
            issues.append(f"第{i}页 status=generated 但无 image_path")
            score -= 1.0

    # 10. 检查 package 是否已保存
    if not package.package_path:
        issues.append("package_path 为空，package 尚未保存")
        score -= 1.0
    else:
        try:
            pkg_p = Path(package.package_path)
            if not pkg_p.is_absolute():
                from project_paths import PROJECT_ROOT
                pkg_p = PROJECT_ROOT / pkg_p
            if not pkg_p.exists():
                issues.append(f"note_package.json 不存在: {package.package_path}")
                score -= 1.0
        except Exception:
            pass

    # 12. 检查视觉DNA
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
