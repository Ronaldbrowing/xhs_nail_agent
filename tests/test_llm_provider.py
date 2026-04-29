import os
import unittest
from unittest.mock import patch

from verticals.nail.note_workflow_schemas import VisualDNA


class LLMProviderTests(unittest.TestCase):
    def _clear_env(self):
        return patch.dict(os.environ, {}, clear=True)

    def test_apimart_provider_defaults_to_official_base_url(self):
        with self._clear_env():
            os.environ["LLM_PROVIDER"] = "apimart"
            os.environ["APIMART_API_KEY"] = "test-apimart-key"

            from src.llm_provider import get_active_provider

            provider = get_active_provider()

            self.assertEqual(provider.provider_id, "apimart")
            self.assertEqual(provider.api_base, "https://api.apimart.ai/v1")
            self.assertEqual(provider.api_key, "test-apimart-key")

    def test_openai_provider_uses_official_defaults(self):
        with self._clear_env():
            os.environ["LLM_PROVIDER"] = "openai"
            os.environ["OPENAI_API_KEY"] = "test-openai-key"

            from src.llm_provider import get_active_provider

            provider = get_active_provider()

            self.assertEqual(provider.provider_id, "openai")
            self.assertIsNone(provider.api_base)
            self.assertEqual(provider.api_key, "test-openai-key")

    def test_text_model_alias_can_be_overridden_by_env(self):
        with self._clear_env():
            os.environ["LLM_PROVIDER"] = "apimart"
            os.environ["APIMART_API_KEY"] = "test-apimart-key"
            os.environ["TEXT_MODEL_COPY_SMALL"] = "claude-sonnet-4.5"

            from src.llm_provider import get_model_name

            self.assertEqual(get_model_name("copy_small"), "claude-sonnet-4.5")

    def test_default_text_model_alias_uses_provider_mapping(self):
        with self._clear_env():
            os.environ["LLM_PROVIDER"] = "apimart"
            os.environ["APIMART_API_KEY"] = "test-apimart-key"

            from src.llm_provider import get_model_name

            self.assertEqual(get_model_name("planner_small"), "gpt-4o-mini")
            self.assertEqual(get_model_name("image_default"), "gpt-image-2")

    def test_image_settings_are_provider_backed(self):
        with self._clear_env():
            os.environ["LLM_PROVIDER"] = "apimart"
            os.environ["APIMART_API_KEY"] = "test-apimart-key"

            from src.llm_provider import get_image_settings

            settings = get_image_settings()

            self.assertEqual(settings["provider_id"], "apimart")
            self.assertEqual(settings["api_base"], "https://api.apimart.ai/v1")
            self.assertEqual(settings["api_key"], "test-apimart-key")
            self.assertEqual(settings["model"], "gpt-image-2")

    def test_unknown_provider_fails_clearly(self):
        with self._clear_env():
            os.environ["LLM_PROVIDER"] = "unknown"

            from src.llm_provider import get_active_provider

            with self.assertRaises(ValueError) as ctx:
                get_active_provider()

            self.assertIn("Unknown LLM provider", str(ctx.exception))

    def test_title_generator_uses_provider_backed_client_and_model_alias(self):
        captured = {}

        class FakeClient:
            def __init__(self, **kwargs):
                captured["client_kwargs"] = kwargs

                class _Completions:
                    @staticmethod
                    def create(**kwargs):
                        captured["request_kwargs"] = kwargs

                        class _Message:
                            content = "标题1 | 标题2 | 标题3 | 标题4 | 标题5 | 标题6 | 标题7 | 标题8 | 标题9 | 标题10"

                        class _Choice:
                            message = _Message()

                        class _Response:
                            choices = [_Choice()]

                        return _Response()

                class _Chat:
                    completions = _Completions()

                self.chat = _Chat()

        with self._clear_env(), patch("openai.OpenAI", FakeClient):
            os.environ["LLM_PROVIDER"] = "apimart"
            os.environ["APIMART_API_KEY"] = "test-apimart-key"
            os.environ["TEXT_MODEL_COPY_SMALL"] = "claude-sonnet-4.5"

            from verticals.nail.title_generator import generate_title_candidates

            titles = generate_title_candidates(
                user_input=type("UserInput", (), {"brief": "夏日蓝色猫眼短甲"})(),
                visual_dna=VisualDNA(),
                count=10,
            )

            self.assertEqual(captured["client_kwargs"]["base_url"], "https://api.apimart.ai/v1")
            self.assertEqual(captured["request_kwargs"]["model"], "claude-sonnet-4.5")
            self.assertEqual(len(titles), 10)

    def test_submit_task_uses_provider_backed_image_settings(self):
        captured = {}

        def fake_post_json(base_url, path, api_key, data, timeout=120):
            captured["base_url"] = base_url
            captured["path"] = path
            captured["api_key"] = api_key
            captured["data"] = data
            return {"data": [{"b64_json": "abc"}]}

        with self._clear_env():
            os.environ["LLM_PROVIDER"] = "apimart"
            os.environ["APIMART_API_KEY"] = "test-apimart-key"
            os.environ["IMAGE_MODEL_DEFAULT"] = "gpt-image-2"

            from gpt_image2_generator import submit_task

            with patch("gpt_image2_generator._post_json", side_effect=fake_post_json):
                submit_task("test prompt", size="1:1")

            self.assertEqual(captured["base_url"], "https://api.apimart.ai/v1")
            self.assertEqual(captured["api_key"], "test-apimart-key")
            self.assertEqual(captured["data"]["model"], "gpt-image-2")


if __name__ == "__main__":
    unittest.main()
