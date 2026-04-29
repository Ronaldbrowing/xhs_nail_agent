"""
NailNoteWorkflow - 小红书美甲图文笔记生产工作流
顶层编排入口
"""
from datetime import datetime
import re
import time

from .note_workflow_schemas import (
    NailNoteUserInput, NailNotePackage, VisualDNA, NotePageSpec,
    NoteGoal,
)
from . import note_templates
from . import visual_dna_builder
from . import note_planner
from . import page_prompt_builder
from . import title_generator
from . import caption_generator
from . import tag_generator
from . import comment_hook_generator
from . import note_qa as note_qa_module
from . import package_writer
from .reference_context import build_reference_context, reference_context_to_diagnostics


def _safe_isoformat(value) -> str:
    try:
        formatted = value.isoformat()
    except Exception:
        formatted = str(value)
    if isinstance(formatted, str):
        return formatted
    return str(formatted)


def _sanitize_note_fragment(value: str, default: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value or "")
    cleaned = cleaned.strip("_")
    return cleaned or default


class NailNoteWorkflow:
    """
    小红书美甲图文笔记生产工作流。
    
    使用方式：
        from verticals.nail.note_workflow import NailNoteWorkflow
        from verticals.nail.note_workflow_schemas import NailNoteUserInput
        
        workflow = NailNoteWorkflow()
        package = workflow.generate_note(
            NailNoteUserInput(
                brief="夏日蓝色猫眼短甲，适合黄皮，显白清透",
                style_id="single_seed_summer_cat_eye_short",
                skin_tone="黄皮",
                nail_length="短甲",
                nail_shape="短方圆",
                note_goal="seed",
                page_count=6,
                generate_images=False,
            )
        )
    """

    def __init__(self):
        pass

    def generate_note(self, user_input: NailNoteUserInput) -> NailNotePackage:
        """
        生成一篇完整的小红书美甲图文笔记。
        
        Args:
            user_input: NailNoteUserInput
        
        Returns:
            NailNotePackage
        """
        brief = user_input.brief or "美甲款式"
        style_id = user_input.style_id or "default"
        note_goal = user_input.note_goal or "seed"
        page_count = user_input.page_count or 6
        workflow_started_at_dt = datetime.now()
        workflow_started_at = _safe_isoformat(workflow_started_at_dt)
        workflow_wall_start = time.perf_counter()
        
        # 日志头部
        print("=" * 70)
        print("💅 Nail Note Workflow - 小红书美甲图文笔记生产")
        print("=" * 70)
        print(f"📝 需求: {brief}")
        print(f"🎯 目标: {note_goal}")
        print(f"📄 页数: {page_count}")
        print()

        # 0. 创建 package 基本结构
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        style_fragment = _sanitize_note_fragment(style_id.replace("/", "_"), "default")
        request_id = _sanitize_note_fragment(str(getattr(user_input, "request_id", "") or ""), "")
        note_id = f"nail_{timestamp}_{style_fragment}"
        if request_id:
            note_id = f"{note_id}_{request_id}"
        output_dir = f"output/{note_id}"
        
        # 初始化 VisualDNA（空，后续步骤填充）
        visual_dna = VisualDNA()
        
        package = NailNotePackage(
            note_id=note_id,
            brief=brief,
            style_id=style_id,
            note_goal=NoteGoal(note_goal) if isinstance(note_goal, str) else note_goal,
            note_template=user_input.note_template,
            visual_dna=visual_dna,
            pages=[],
            output_dir=output_dir,
            success=False,
            partial_failure=False,
        )
        package.diagnostics["page_timings"] = []
        package.diagnostics["timing"] = {
            "workflow_started_at": workflow_started_at,
            "workflow_finished_at": None,
            "workflow_duration_sec": None,
            "image_generation_duration_sec": 0.0,
            "avg_page_generation_sec": 0.0,
        }
        package.diagnostics["generation_mode"] = {
            "concurrency": "sequential",
            "max_workers": max(1, min(int(getattr(user_input, "max_workers", 1) or 1), 3)),
            "quality": getattr(user_input, "quality", "final") or "final",
            "aspect": getattr(user_input, "aspect", "3:4") or "3:4",
        }

        reference_context = build_reference_context(user_input, task="poster")
        package.diagnostics["reference"] = reference_context_to_diagnostics(reference_context)

        # 1. 构建 VisualDNA
        print("[视觉DNA] 🔄 构建视觉DNA...")
        try:
            dna = visual_dna_builder.build_visual_dna(
                user_input,
                reference_image_path=reference_context.reference_image_path,
                case_id=reference_context.case_id,
                reference_context=reference_context,
            )
            package.visual_dna = dna
            
            dna_desc = []
            if dna.skin_tone:
                dna_desc.append(dna.skin_tone)
            if dna.nail_length:
                dna_desc.append(dna.nail_length)
            if dna.nail_shape:
                dna_desc.append(dna.nail_shape)
            if dna.main_color:
                dna_desc.append(dna.main_color)
            if dna.finish:
                dna_desc.append(dna.finish)
            
            print(f"[视觉DNA] ✅ 构建完成：{' / '.join(dna_desc) if dna_desc else '完成'}")
        except Exception as e:
            print(f"[视觉DNA] ⚠️ 构建失败: {e}，使用默认DNA")
            package.diagnostics["visual_dna_error"] = str(e)
        print()

        # 2. 获取页面模板
        print("[笔记规划] 🔄 生成页面结构...")
        try:
            role_goal_pairs = note_templates.get_page_role_goals(note_goal, page_count)
            print(f"[笔记规划] ✅ 已生成 {len(role_goal_pairs)} 页结构：{[r.value for r, _ in role_goal_pairs]}")
        except Exception as e:
            print(f"[笔记规划] ⚠️ 获取模板失败: {e}")
            role_goal_pairs = note_templates.get_page_role_goals("seed", 6)
        print()

        # 3. 规划页面
        print("[页面规划] 🔄 规划每页内容...")
        try:
            pages = note_planner.plan_note_pages(user_input, package.visual_dna, role_goal_pairs)
            package.pages = pages
            print(f"[页面规划] ✅ 已生成 {len(pages)} 页规划")
        except Exception as e:
            print(f"[页面规划] ⚠️ 页面规划失败: {e}")
            package.partial_failure = True
            package.diagnostics["page_planning_error"] = str(e)
            # 使用 fallback
            pages = []
            for i, (role, goal) in enumerate(role_goal_pairs):
                pages.append(NotePageSpec(
                    page_no=i+1,
                    role=role,
                    goal=goal,
                    visual_brief=f"展示{role.value}",
                    status="planned",
                ))
            package.pages = pages
        print()

        # 4. 编译每页 Prompt
        print("[页面Prompt] 🔄 编译每页生成Prompt...")
        prompt_ready_count = 0
        for page in pages:
            try:
                page_prompt_builder.build_page_prompt(page, package.visual_dna, user_input)
                if page.prompt:
                    prompt_ready_count += 1
            except Exception as e:
                print(f"[页面Prompt] ⚠️ page_{page.page_no} 编译失败: {e}")
                page.issues.append(str(e))
        print(f"[页面Prompt] ✅ {prompt_ready_count}/{len(pages)} 页 Prompt 准备就绪")
        print()

        # 5. 生成标题
        print("[标题生成] 🔄 生成标题候选...")
        title_count = 0
        try:
            if user_input.generate_copy:
                titles = title_generator.generate_title_candidates(user_input, package.visual_dna, count=12)
                package.title_candidates = titles
                if titles:
                    package.selected_title = titles[0]
                    title_count = len(titles)
        except Exception as e:
            print(f"[标题生成] ⚠️ 生成失败: {e}")
            package.diagnostics["title_error"] = str(e)
        print(f"[标题生成] ✅ 已生成 {title_count} 个标题候选")
        if package.selected_title:
            print(f"   选定为: {package.selected_title}")
        print()

        # 6. 生成正文
        print("[正文生成] 🔄 生成笔记正文...")
        body_ok = False
        try:
            if user_input.generate_copy:
                body = caption_generator.generate_caption(user_input, package.visual_dna, pages)
                if body and len(body) > 50:
                    package.body = body
                    body_ok = True
        except Exception as e:
            print(f"[正文生成] ⚠️ 生成失败: {e}")
            package.diagnostics["caption_error"] = str(e)
        print(f"[正文生成] {'✅ ' if body_ok else '⚠️ '}正文 {'生成完成' if body_ok else '生成失败或过短'}")
        print()

        # 7. 生成 TAG
        print("[TAG生成] 🔄 生成标签...")
        tag_count = 0
        try:
            if user_input.generate_tags:
                tags = tag_generator.generate_tags(user_input, package.visual_dna, count=20)
                if tags:
                    package.tags = tags
                    tag_count = len(tags)
        except Exception as e:
            print(f"[TAG生成] ⚠️ 生成失败: {e}")
            package.diagnostics["tag_error"] = str(e)
        print(f"[TAG生成] ✅ 已生成 {tag_count} 个TAG")
        print()

        # 8. 生成评论钩子
        print("[评论钩子] 🔄 生成评论互动钩子...")
        hook_count = 0
        try:
            if user_input.generate_copy:
                hooks = comment_hook_generator.generate_comment_hooks(user_input, package.visual_dna, count=4)
                if hooks:
                    package.comment_hooks = hooks
                    hook_count = len(hooks)
        except Exception as e:
            print(f"[评论钩子] ⚠️ 生成失败: {e}")
            package.diagnostics["hook_error"] = str(e)
        print(f"[评论钩子] ✅ 已生成 {hook_count} 个评论钩子")
        print()

        # 9. 生成图片（如果需要）
        if user_input.generate_images:
            print("[图片生成] 🔄 开始生成图片...")
            image_generation_start = time.perf_counter()
            try:
                from .note_image_generator import generate_note_images
                generate_note_images(package, user_input, reference_context=reference_context)
                image_generation_duration_sec = round(time.perf_counter() - image_generation_start, 3)
                page_timings = package.diagnostics.get("page_timings", [])
                avg_page_generation_sec = 0.0
                if page_timings:
                    avg_page_generation_sec = round(
                        sum(item.get("duration_sec", 0.0) for item in page_timings) / len(page_timings),
                        3,
                    )
                package.diagnostics["timing"]["image_generation_duration_sec"] = image_generation_duration_sec
                package.diagnostics["timing"]["avg_page_generation_sec"] = avg_page_generation_sec
                package.diagnostics["generation_mode"]["concurrency"] = (
                    "parallel" if package.diagnostics["generation_mode"]["max_workers"] > 1 else "sequential"
                )
                print(f"[图片生成] ✅ 图片生成完成")
                for page in package.pages:
                    if page.status == "generated":
                        print(f"   page_{page.page_no}: {page.image_path}")
                    elif page.status == "failed":
                        print(f"   page_{page.page_no}: ❌ FAILED")
            except Exception as e:
                print(f"[图片生成] ⚠️ 生成失败: {e}")
                package.diagnostics["image_gen_error"] = str(e)
                package.partial_failure = True
        else:
            print("[图片生成] ⏭️ 已跳过（generate_images=False）")
        print()

        # 10. 最终结果计算
        # 检查封面页状态
        cover_page = package.pages[0] if package.pages else None
        cover_failed = cover_page and cover_page.status == "failed"

        # 检查内页失败（用于 partial_failure）
        inner_pages_failed = sum(
            1 for p in package.pages[1:] if p.status == "failed"
        )

        if user_input.generate_images:
            # generate_images=True：图片必须生成成功
            package.success = (
                len(package.pages) >= 6
                and len(package.title_candidates) >= 10
                and len(package.tags) >= 15
                and len(package.comment_hooks) >= 3
                and bool(package.body)
                and cover_page is not None
                and cover_page.status == "generated"
                and cover_page.image_path is not None
            )
            # 封面失败时 partial_failure=True，内页失败时 partial_failure=True
            if cover_failed or inner_pages_failed > 0:
                package.partial_failure = True
        else:
            # generate_images=False：不要求图片
            package.success = (
                len(package.pages) >= 6
                and len(package.title_candidates) >= 10
                and len(package.tags) >= 15
                and len(package.comment_hooks) >= 3
                and bool(package.body)
            )

        print(f"[结果] success={package.success} partial_failure={package.partial_failure}")
        if cover_failed:
            print(f"[结果] ⚠️ 封面页生成失败")
        if inner_pages_failed > 0:
            print(f"[结果] ⚠️ {inner_pages_failed} 个内页生成失败")
        print()

        # 11. 先保存一次 package，确保后续 QA 能检查 package_path
        print("[发布包] 🔄 保存发布包...")
        try:
            ok = package_writer.write_note_package(package, output_dir)
            if ok:
                print(f"[发布包] ✅ note_package.json 已保存: {package.package_path}")
                print(f"[发布包] ✅ archive.json 已保存: {package.archive_path}")
            else:
                print(f"[发布包] ⚠️ 保存失败")
        except Exception as e:
            print(f"[发布包] ⚠️ 保存异常: {e}")
            package.diagnostics["package_writer_error"] = str(e)
        print()

        # 12. QA 检查（保存之后；分数写回 diagnostics 后再落盘一次）
        print("[QA检查] 🔄 运行质量检查...")
        try:
            qa_result = note_qa_module.qa_note_package(package, generate_images=user_input.generate_images)
            print(f"[QA检查] {'✅ PASS' if qa_result['passed'] else '⚠️ WARN'} score={qa_result['score']}")
            if qa_result['issues']:
                for issue in qa_result['issues']:
                    print(f"   - {issue}")
            if qa_result.get("warnings"):
                for warning in qa_result["warnings"]:
                    print(f"   ! {warning}")
            package.diagnostics["qa_score"] = qa_result['score']
            package.diagnostics["qa"] = qa_result
            ok = package_writer.write_note_package(package, output_dir)
            if not ok:
                print("[QA检查] ⚠️ QA 结果回写失败")
        except Exception as e:
            print(f"[QA检查] ⚠️ 检查失败: {e}")
            package.diagnostics["qa_error"] = str(e)
            ok = package_writer.write_note_package(package, output_dir)
            if not ok:
                print("[QA检查] ⚠️ QA 异常信息回写失败")
        print()

        workflow_finished_at = _safe_isoformat(datetime.now())
        workflow_duration_sec = round(time.perf_counter() - workflow_wall_start, 3)
        package.diagnostics["timing"]["workflow_finished_at"] = workflow_finished_at
        package.diagnostics["timing"]["workflow_duration_sec"] = workflow_duration_sec
        package_writer.write_note_package(package, output_dir)

        print("=" * 70)
        print(f"💅 生成完成 | success={package.success} | partial_failure={package.partial_failure}")
        print(f"📁 输出目录: {package.output_dir}")
        print(f"📦 发布包: {package.package_path}")
        print("=" * 70)

        return package
