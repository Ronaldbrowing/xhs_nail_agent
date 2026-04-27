from pathlib import Path
import sys

_SKILL_ROOT = Path.home() / ".hermes" / "agents" / "multi-agent-image"
if str(_SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(_SKILL_ROOT))

class MultiAgentImageRunner:
    """
    Adapter for connecting verticals.nail.NailWorkflow to multi-agent-image.
    It calls orchestrator_v2.run() with the compiled nail image prompt.
    """

    def __init__(self, use_reference=False):
        self.use_reference = use_reference

    def generate(self, brief, task="poster", direction="balanced", aspect="3:4", quality=None, dna_summary=None):
        try:
            from orchestrator_v2 import run
        except Exception:
            try:
                from orchestrator_v2 import run
            except Exception as e:
                return {
                    "ok": False,
                    "error": "Failed to import orchestrator_v2.run",
                    "detail": str(e),
                }

        try:
            result = run(
                brief,
                task=task,
                direction=direction,
                aspect=aspect,
                quality=quality,
                use_reference=self.use_reference,
                precompiled_brief=True,
                dna_summary=dna_summary,
            )

            return {
                "ok": True,
                "result": result,
                "requested_params": {
                    "task": task,
                    "direction": direction,
                    "aspect": aspect,
                    "quality": quality,
                    "precompiled_brief": True,
                    "dna_summary_included": bool(dna_summary),
                },
            }

        except Exception as e:
            return {
                "ok": False,
                "error": "Image generation failed",
                "detail": str(e),
                "requested_params": {
                    "task": task,
                    "direction": direction,
                    "aspect": aspect,
                    "quality": quality,
                    "precompiled_brief": True,
                    "dna_summary_included": bool(dna_summary),
                },
            }
