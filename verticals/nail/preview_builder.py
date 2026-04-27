from typing import Optional
from .schemas import PreviewPayload, PromptBundle, NailStyle, ReferenceDNA

def build_preview(bundle: PromptBundle, style: NailStyle, dna: Optional[ReferenceDNA]) -> PreviewPayload:
    dna_summary = None
    if dna:
        dna_summary = {
            "subject": dna.subject,
            "hand_model": dna.hand_model,
            "nail_shape": dna.nail_shape,
            "nail_length": dna.nail_length,
            "dominant_colors": dna.dominant_colors,
            "finish_types": dna.finish_types,
            "decorations": dna.decorations,
            "composition": dna.composition,
            "background": dna.background,
            "lighting": dna.lighting,
            "mood": dna.mood,
            "title_area_hint": dna.title_area_hint,
            "main_visual_identity": dna.main_visual_identity
        }

    return PreviewPayload(
        cover_prompt=bundle.image_prompt,
        titles=bundle.title_candidates,
        bodies=bundle.body_candidates,
        tags=bundle.tag_candidates,
        selected_style=style.style_name,
        dna_summary=dna_summary
    )
