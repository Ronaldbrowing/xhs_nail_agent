from .schemas import UserInput, PromptBundle
from .style_matcher import match_style
from .dna_extractor import extract_dna_from_model
from .prompt_builder import build_image_prompt
from .copy_generator import generate_copy
from .preview_builder import build_preview

class NailWorkflow:
    def __init__(self, llm_client=None, multimodal_client=None, image_runner=None):
        self.llm_client = llm_client
        self.multimodal_client = multimodal_client
        self.image_runner = image_runner

    def prepare(self, user_input: UserInput):
        style = match_style(user_input)

        dna = None
        if user_input.reference_image_path:
            dna = extract_dna_from_model(
                image_path=user_input.reference_image_path,
                multimodal_client=self.multimodal_client
            )

        image_prompt = build_image_prompt(user_input, style, dna)
        copy_data, copy_prompt = generate_copy(self.llm_client, user_input, style, dna)

        bundle = PromptBundle(
            final_brief=user_input.brief,
            image_prompt=image_prompt,
            copy_prompt=copy_prompt,
            title_candidates=copy_data.get("titles", []),
            body_candidates=copy_data.get("bodies", []),
            tag_candidates=copy_data.get("tags", []),
            debug_info={
                "style_id": style.style_id,
                "style_name": style.style_name,
                "scene_type": style.scene_type,
                "dna_used": dna is not None
            }
        )

        preview = build_preview(bundle, style, dna)
        return {"style": style, "dna": dna, "bundle": bundle, "preview": preview}

    def generate_image(self, prepared_result):
        if self.image_runner is None:
            return {"ok": False, "error": "No image_runner configured"}
        style = prepared_result["style"]
        bundle = prepared_result["bundle"]
        return self.image_runner.generate(
            brief=bundle.image_prompt,
            task=style.task,
            direction=style.direction,
            aspect=style.aspect
        )
