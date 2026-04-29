import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from verticals.nail.note_workflow_schemas import NailNoteUserInput


class NailReferenceContextTests(unittest.TestCase):
    def setUp(self):
        self._temp_dir = Path(tempfile.mkdtemp(prefix="nail_ref_ctx_"))

    def tearDown(self):
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    def test_conflicting_reference_inputs_raise_value_error(self):
        from verticals.nail.reference_context import build_reference_context

        user_input = NailNoteUserInput(
            brief="test",
            reference_image_path="output/ref.png",
            case_id="case_001",
        )

        with self.assertRaises(ValueError):
            build_reference_context(user_input)

    def test_local_path_reference_context_resolves_existing_file(self):
        from verticals.nail.reference_context import build_reference_context

        image_path = self._temp_dir / "ref.png"
        image_path.write_bytes(b"fake image bytes")
        user_input = NailNoteUserInput(
            brief="test",
            reference_image_path=str(image_path),
            case_id=None,
        )

        context = build_reference_context(user_input)

        self.assertEqual(context.source_type, "local_path")
        self.assertEqual(context.case_id, None)
        self.assertEqual(Path(context.resolved_image_path), image_path.resolve())
        self.assertTrue(context.has_reference)

    def test_case_id_reference_context_resolves_metadata_and_image(self):
        from verticals.nail.reference_context import build_reference_context

        image_path = self._temp_dir / "case_image.png"
        image_path.write_bytes(b"fake image bytes")
        metadata = {
            "case_id": "case_test_001",
            "brief": "夏日蓝色猫眼短甲",
            "prompt": "清透、猫眼、黄皮显白",
            "params": {"task": "poster", "aspect": "3:4", "direction": "balanced"},
            "tags": ["蓝色", "猫眼"],
            "rating": 9,
        }
        user_input = NailNoteUserInput(
            brief="test",
            reference_image_path=None,
            case_id="case_test_001",
        )

        with patch("verticals.nail.reference_context.get_case_image_path", return_value=str(image_path)), \
             patch("verticals.nail.reference_context.get_case_metadata", return_value=metadata):
            context = build_reference_context(user_input)

        self.assertEqual(context.source_type, "case_id")
        self.assertEqual(context.case_id, "case_test_001")
        self.assertEqual(Path(context.resolved_image_path), image_path.resolve())
        self.assertEqual(context.metadata["case_id"], "case_test_001")
        self.assertTrue(context.dna_summary)
        self.assertTrue(context.has_reference)
