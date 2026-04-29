"""
图片运行适配器 - 桥接到 orchestrator_v2.run()
修复: 不再使用 Path.home()，直接使用项目相对路径
"""
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


class MultiAgentImageRunner:
    """
    Adapter for connecting NailNoteWorkflow to orchestrator_v2.
    It calls orchestrator_v2.run() with the compiled nail image prompt.
    """

    def __init__(self, use_reference=False):
        self.use_reference = use_reference

    def generate(self, brief, task="poster", direction="balanced", aspect="3:4",
                 quality=None, dna_summary=None, reference_image_path=None):
        """
        调用 orchestrator_v2.run() 生成图片。
        
        Args:
            brief: 图片生成描述（prompt）
            task: 任务类型
            direction: 风格方向
            aspect: 宽高比
            quality: 质量设置
            dna_summary: DNA摘要
            reference_image_path: 参考图路径（相对路径）
        
        Returns:
            dict with ok/result/error
        """
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
                reference_image_path=reference_image_path,
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
                    "reference_image_path": reference_image_path,
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
