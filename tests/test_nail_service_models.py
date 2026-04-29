import unittest

from verticals.nail.note_workflow_schemas import NailNotePackage, NoteGoal, NotePageSpec, PageRole, VisualDNA
from verticals.nail.service.schemas import NailNoteCreateRequest


class NailServiceModelTests(unittest.TestCase):
    def _fake_package(self):
        return NailNotePackage(
            note_id="note_001",
            brief="夏日蓝色猫眼短甲",
            style_id="style_001",
            note_goal=NoteGoal.seed,
            visual_dna=VisualDNA(main_color="蓝色"),
            pages=[
                NotePageSpec(
                    page_no=1,
                    role=PageRole.cover,
                    goal="cover",
                    visual_brief="visual",
                    prompt="prompt",
                    status="generated",
                    image_path="output/note_001/page_01_cover.png",
                    used_reference=False,
                )
            ],
            title_candidates=["title_0"],
            selected_title="title_0",
            body="这是一段足够长的正文。" * 8,
            tags=["tag_0"] * 15,
            comment_hooks=["hook_0", "hook_1", "hook_2"],
            output_dir="output/note_001",
            package_path="output/note_001/note_package.json",
            success=True,
            partial_failure=False,
            diagnostics={"qa_score": 9.5},
        )

    def test_request_can_convert_to_workflow_user_input(self):
        request = NailNoteCreateRequest(
            brief="夏日蓝色猫眼短甲",
            page_count=6,
            generate_images=False,
            reference_image_path=None,
            case_id=None,
            max_workers=2,
        )

        user_input = request.to_user_input()

        self.assertEqual(user_input.brief, "夏日蓝色猫眼短甲")
        self.assertEqual(user_input.page_count, 6)
        self.assertFalse(user_input.generate_images)
        self.assertEqual(user_input.max_workers, 2)

    def test_service_response_contains_request_id_status_and_diagnostics(self):
        from verticals.nail.service.nail_note_service import build_create_response

        package = self._fake_package()
        response = build_create_response(
            request_id="req_123",
            package=package,
            status="succeeded",
            errors=[],
        )

        self.assertEqual(response.request_id, "req_123")
        self.assertEqual(response.status, "succeeded")
        self.assertTrue(response.success)
        self.assertEqual(response.qa_score, 9.5)
        self.assertIn("qa_score", response.diagnostics)
