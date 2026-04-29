import json
import shutil
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock

from project_paths import PROJECT_ROOT, resolve_project_path, to_project_relative
from verticals.nail.note_image_generator import _generate_single_page
from verticals.nail.note_qa import qa_note_package
from verticals.nail.note_workflow import NailNoteWorkflow
from verticals.nail.note_workflow_schemas import (
    NailNotePackage,
    NailNoteUserInput,
    NoteGoal,
    NotePageSpec,
    PageRole,
    VisualDNA,
)
from verticals.nail.schemas import UserInput


def _make_pages(count=6):
    roles = [
        PageRole.cover,
        PageRole.detail_closeup,
        PageRole.skin_tone_fit,
        PageRole.style_breakdown,
        PageRole.scene_mood,
        PageRole.save_summary,
    ]
    pages = []
    for page_no in range(1, count + 1):
        role = roles[page_no - 1]
        pages.append(
            NotePageSpec(
                page_no=page_no,
                role=role,
                goal=f"goal_{page_no}",
                visual_brief=f"visual_{page_no}",
                prompt=f"prompt_{page_no}",
                status="planned",
            )
        )
    return pages


class NailAcceptanceRegressionTests(unittest.TestCase):
    def setUp(self):
        self._cleanup_dirs = []

    def tearDown(self):
        for path in self._cleanup_dirs:
            shutil.rmtree(path, ignore_errors=True)

    def _register_cleanup_dir(self, path: Path) -> Path:
        self._cleanup_dirs.append(path)
        return path

    def _make_output_dir(self, prefix: str) -> Path:
        path = PROJECT_ROOT / "output" / f"{prefix}_{uuid.uuid4().hex[:8]}"
        path.mkdir(parents=True, exist_ok=True)
        return self._register_cleanup_dir(path)

    def _fake_visual_dna(self):
        return VisualDNA(
            skin_tone="黄皮",
            nail_length="短甲",
            nail_shape="短方圆",
            main_color="蓝色",
            finish="猫眼",
        )

    def _build_page_prompt(self, page, visual_dna, user_input):
        page.prompt = page.prompt or f"prompt_{page.page_no}"
        return page

    def _fake_generate_images(self, package, user_input, reference_context=None):
        note_dir = resolve_project_path(package.output_dir)
        note_dir.mkdir(parents=True, exist_ok=True)
        for page in package.pages:
            image_path = note_dir / f"page_{page.page_no:02d}.png"
            image_path.write_bytes(b"fake image bytes")
            page.image_path = to_project_relative(image_path)
            page.status = "generated"
        return package

    def test_userinput_accepts_nail_workflow_fields(self):
        user_input = UserInput(
            brief="夏日蓝色猫眼短甲",
            style_id="single_seed_summer_cat_eye_short",
            note_goal="seed",
            page_count=6,
            generate_images=False,
        )

        self.assertEqual(user_input.page_count, 6)
        self.assertEqual(user_input.note_goal, "seed")
        self.assertFalse(user_input.generate_images)
        self.assertIsInstance(user_input, NailNoteUserInput)

    def test_generate_note_without_images_acceptance(self):
        workflow = NailNoteWorkflow()
        user_input = UserInput(
            brief="夏日蓝色猫眼短甲，适合黄皮，显白清透",
            style_id="single_seed_summer_cat_eye_short",
            skin_tone="黄皮",
            nail_length="短甲",
            nail_shape="短方圆",
            note_goal="seed",
            page_count=6,
            generate_images=False,
        )

        pages = _make_pages()
        timestamp = f"20260429_{uuid.uuid4().hex[:8]}"

        with patch("verticals.nail.note_workflow.visual_dna_builder.build_visual_dna", return_value=self._fake_visual_dna()), \
             patch("verticals.nail.note_workflow.note_templates.get_page_role_goals", return_value=[(page.role, page.goal) for page in pages]), \
             patch("verticals.nail.note_workflow.note_planner.plan_note_pages", return_value=pages), \
             patch("verticals.nail.note_workflow.page_prompt_builder.build_page_prompt", side_effect=self._build_page_prompt), \
             patch("verticals.nail.note_workflow.title_generator.generate_title_candidates", return_value=[f"title_{i}" for i in range(12)]), \
             patch("verticals.nail.note_workflow.caption_generator.generate_caption", return_value="这是一段足够长的正文。" * 12), \
             patch("verticals.nail.note_workflow.tag_generator.generate_tags", return_value=[f"tag_{i}" for i in range(15)]), \
             patch("verticals.nail.note_workflow.comment_hook_generator.generate_comment_hooks", return_value=[f"hook_{i}" for i in range(3)]), \
             patch("verticals.nail.note_workflow.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = timestamp
            package = workflow.generate_note(user_input)
            self._register_cleanup_dir(resolve_project_path(package.output_dir))

        self.assertTrue(package.success)
        self.assertFalse(package.partial_failure)
        self.assertEqual(package.diagnostics.get("qa_score"), 10.0)
        self.assertTrue(resolve_project_path(package.package_path).exists())

    def test_generate_note_with_images_runs_qa_after_save_and_persists_diagnostics(self):
        workflow = NailNoteWorkflow()
        user_input = NailNoteUserInput(
            brief="夏日蓝色猫眼短甲，适合黄皮，显白清透",
            style_id="single_seed_summer_cat_eye_short",
            note_goal="seed",
            page_count=6,
            generate_images=True,
        )

        pages = _make_pages()
        qa_observation = {}
        timestamp = f"20260429_{uuid.uuid4().hex[:8]}"

        def fake_qa(package, generate_images=True):
            qa_observation["package_path"] = package.package_path
            qa_observation["package_exists"] = bool(package.package_path) and resolve_project_path(package.package_path).exists()
            return {"passed": True, "score": 9.5, "issues": []}

        with patch("verticals.nail.note_workflow.visual_dna_builder.build_visual_dna", return_value=self._fake_visual_dna()), \
             patch("verticals.nail.note_workflow.note_templates.get_page_role_goals", return_value=[(page.role, page.goal) for page in pages]), \
             patch("verticals.nail.note_workflow.note_planner.plan_note_pages", return_value=pages), \
             patch("verticals.nail.note_workflow.page_prompt_builder.build_page_prompt", side_effect=self._build_page_prompt), \
             patch("verticals.nail.note_workflow.title_generator.generate_title_candidates", return_value=[f"title_{i}" for i in range(12)]), \
             patch("verticals.nail.note_workflow.caption_generator.generate_caption", return_value="这是一段足够长的正文。" * 12), \
             patch("verticals.nail.note_workflow.tag_generator.generate_tags", return_value=[f"tag_{i}" for i in range(15)]), \
             patch("verticals.nail.note_workflow.comment_hook_generator.generate_comment_hooks", return_value=[f"hook_{i}" for i in range(3)]), \
             patch("verticals.nail.note_image_generator.generate_note_images", side_effect=self._fake_generate_images), \
             patch("verticals.nail.note_workflow.note_qa_module.qa_note_package", side_effect=fake_qa), \
             patch("verticals.nail.note_workflow.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = timestamp
            package = workflow.generate_note(user_input)
            self._register_cleanup_dir(resolve_project_path(package.output_dir))

        self.assertTrue(qa_observation["package_exists"])
        self.assertTrue(resolve_project_path(package.package_path).exists())

        saved_package = json.loads(resolve_project_path(package.package_path).read_text(encoding="utf-8"))
        self.assertEqual(saved_package["diagnostics"]["qa_score"], 9.5)

    def test_case_id_is_forwarded_to_orchestrator_run(self):
        note_dir = self._make_output_dir("case_id_forward")
        source_image = note_dir / "source.png"
        source_image.write_bytes(b"fake image bytes")
        page = NotePageSpec(
            page_no=1,
            role=PageRole.cover,
            goal="cover",
            visual_brief="cover visual",
            prompt="prompt_1",
        )
        user_input = NailNoteUserInput(
            brief="夏日蓝色猫眼短甲",
            case_id="case_test_001",
            generate_images=True,
        )

        run_kwargs = {}

        def fake_run(*args, **kwargs):
            run_kwargs.update(kwargs)
            return {"filepath": str(source_image)}

        with patch("orchestrator_v2.run", side_effect=fake_run):
            updated_page, _ = _generate_single_page(page, user_input, note_dir)

        self.assertEqual(run_kwargs["case_id"], "case_test_001")
        self.assertTrue(run_kwargs["use_reference"])
        self.assertEqual(run_kwargs["save_case"], False)
        self.assertEqual(run_kwargs["archive_mode"], "note_only")
        self.assertEqual(updated_page.status, "generated")
        self.assertTrue(updated_page.image_path)

    def test_orchestrator_skip_case_library_when_save_case_false(self):
        import orchestrator_v2

        with patch("orchestrator_v2.step3_image_generator", return_value={"status": "success", "filepath": __file__, "url": None, "used_reference": False}), \
             patch("orchestrator_v2.step4_qa", return_value={"verdict": "PASS", "score": 9.0, "approval": True}), \
             patch("orchestrator_v2.step5_metadata") as mock_step5, \
             patch("orchestrator_v2.add_case") as mock_add_case:
            result = orchestrator_v2.run(
                user_input="test prompt",
                use_reference=False,
                task="poster",
                direction="balanced",
                aspect="3:4",
                quality="draft",
                precompiled_brief=True,
                save_case=False,
                archive=False,
                archive_mode="none",
            )

        self.assertTrue(result["success"])
        mock_add_case.assert_not_called()
        mock_step5.assert_not_called()

    def test_orchestrator_archive_mode_none_skips_archive_write(self):
        import orchestrator_v2

        with patch("orchestrator_v2.step3_image_generator", return_value={"status": "success", "filepath": __file__, "url": None, "used_reference": False}), \
             patch("orchestrator_v2.step4_qa", return_value={"verdict": "PASS", "score": 9.0, "approval": True}), \
             patch("orchestrator_v2.step5_metadata") as mock_step5, \
             patch("orchestrator_v2.add_case") as mock_add_case:
            result = orchestrator_v2.run(
                user_input="test prompt",
                use_reference=False,
                task="poster",
                direction="balanced",
                aspect="3:4",
                quality="draft",
                precompiled_brief=True,
                save_case=False,
                archive=True,
                archive_mode="none",
            )

        self.assertTrue(result["success"])
        mock_step5.assert_not_called()
        mock_add_case.assert_not_called()

    def test_qa_checks_generated_page_image_paths(self):
        assets_dir = self._make_output_dir("qa_generated_paths")
        cover_path = assets_dir / "cover.png"
        cover_path.write_bytes(b"fake image bytes")

        package = NailNotePackage(
            note_id="qa_case",
            brief="brief",
            style_id="style",
            note_goal=NoteGoal.seed,
            visual_dna=self._fake_visual_dna(),
            pages=[
                NotePageSpec(
                    page_no=1,
                    role=PageRole.cover,
                    goal="cover",
                    visual_brief="cover visual",
                    prompt="prompt_1",
                    status="generated",
                    image_path=to_project_relative(cover_path),
                ),
                NotePageSpec(
                    page_no=2,
                    role=PageRole.detail_closeup,
                    goal="detail",
                    visual_brief="detail visual",
                    prompt="prompt_2",
                    status="generated",
                    image_path="output/does_not_exist.png",
                ),
            ],
            title_candidates=[f"title_{i}" for i in range(10)],
            selected_title="title_0",
            body="这是一段足够长的正文。" * 12,
            tags=[f"tag_{i}" for i in range(15)],
            comment_hooks=[f"hook_{i}" for i in range(3)],
            output_dir=to_project_relative(assets_dir),
            package_path=to_project_relative(assets_dir / "note_package.json"),
        )

        (assets_dir / "note_package.json").write_text("{}", encoding="utf-8")
        qa_result = qa_note_package(package, generate_images=True)

        self.assertFalse(qa_result["passed"])
        self.assertTrue(any("第2页 image_path 不存在" in issue for issue in qa_result["issues"]))

    def test_qa_reports_failed_cover_for_mock_package(self):
        package = NailNotePackage(
            note_id="qa_cover_failed",
            brief="brief",
            style_id="style",
            note_goal=NoteGoal.seed,
            visual_dna=self._fake_visual_dna(),
            pages=[
                NotePageSpec(
                    page_no=1,
                    role=PageRole.cover,
                    goal="cover",
                    visual_brief="cover visual",
                    prompt="prompt_1",
                    status="failed",
                    issues=["mock cover failure"],
                ),
            ],
            title_candidates=[f"title_{i}" for i in range(10)],
            selected_title="title_0",
            body="这是一段足够长的正文。" * 12,
            tags=[f"tag_{i}" for i in range(15)],
            comment_hooks=[f"hook_{i}" for i in range(3)],
            output_dir="output/mock_cover_failed",
            package_path="output/mock_cover_failed/note_package.json",
        )

        qa_result = qa_note_package(package, generate_images=True)

        self.assertFalse(qa_result["passed"])
        self.assertIn("封面页生成失败", qa_result["issues"])


if __name__ == "__main__":
    unittest.main()
