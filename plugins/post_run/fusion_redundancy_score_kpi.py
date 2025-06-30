from core.models import PluginResult, TestContext
from core.post_run_plugin import PostRunPlugin
import json
from pathlib import Path

class FusionRedundancyScorePlugin(PostRunPlugin):
    """
    Calculates the Fusion Redundancy Score:
    Measures how often both camera and radar contribute to a fused detection.
    """

    def execute(self, context: TestContext) -> PluginResult:
        threshold = self.config.get("min_redundancy_score", 0.5)  # default 50%
        scenario_path = context.data_path  # TODO pass data_path by Scenario object not by contex
        total_fused_objects = 0
        redundant_fusions = 0

        try:
            with open(scenario_path, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    for obj in entry.get("fused_objects", []):
                        source_classes = obj.get("source_classes", {})
                        if "camera" in source_classes and "radar" in source_classes:
                            redundant_fusions += 1
                        total_fused_objects += 1

            if total_fused_objects == 0:
                return PluginResult(success=False, message="No fused objects found")

            score = redundant_fusions / total_fused_objects
            success = score >= threshold
            message = (
                f"Fusion Redundancy Score {score:.2f} is above threshold {threshold:.2f}"
                if success else
                f"Fusion Redundancy Score {score:.2f} is below threshold {threshold:.2f}"
            )

            return PluginResult(
                success=success,
                message=message,
                metrics={
                    "fusion_redundancy_score": {
                        "score": score,
                        "redundant_fusions": redundant_fusions,
                        "total_fused_objects": total_fused_objects,
                        "threshold": threshold
                    }
                }
            )

        except Exception as e:
            return PluginResult(success=False, message=str(e))
