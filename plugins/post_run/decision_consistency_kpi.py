from core.models import PluginResult, TestContext
from core.post_run_plugin import PostRunPlugin
import json
from pathlib import Path


class DecisionConsistencyScorePlugin(PostRunPlugin):
    def execute(self, context: TestContext) -> PluginResult:
        threshold = self.config.get("consistency_threshold", 0.95)
        scenario_path = context.data_path  # TODO pass data_path by Scenario object not by contex

        total = 0
        consistent = 0

        try:
            with open(scenario_path, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    fused_objects = entry.get("fused_objects", [])
                    for obj in fused_objects:
                        fused_class = obj.get("class")
                        source_classes = obj.get("source_classes", {})

                        camera_class = source_classes.get("camera")
                        radar_class = source_classes.get("radar")

                        if fused_class is None:
                            continue

                        total += 1
                        if fused_class in {camera_class, radar_class}:
                            consistent += 1

            if total == 0:
                return PluginResult(success=False, message="No valid data for evaluation", metrics={})

            score = consistent / total
            success = score >= threshold
            message = (
                f"Decision consistency score {score:.4f} meets threshold {threshold}"
                if success else
                f"Decision consistency score {score:.4f} below threshold {threshold}"
            )

            return PluginResult(
                success=success,
                message=message,
                metrics={
                    "decision_consistency_score": {
                        "score": score,
                        "threshold": threshold,
                        "consistent": consistent,
                        "total": total
                    }
                }
            )

        except Exception as e:
            return PluginResult(success=False, message=str(e), metrics={})
