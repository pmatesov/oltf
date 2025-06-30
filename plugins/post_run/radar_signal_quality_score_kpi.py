from core.models import PluginResult, TestContext
from core.post_run_plugin import PostRunPlugin
import json


class RadarSignalQualityScorePlugin(PostRunPlugin):
    def execute(self, context: TestContext) -> PluginResult:
        threshold = self.config.get("min_avg_signal_strength", 0.8)  # Default threshold
        scenario_path = context.data_path  # TODO pass data_path by Scenario object not by contex
        signal_strengths = []

        try:
            with open(scenario_path, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    radar_points = entry.get("points", [])

                    for point in radar_points:
                        signal = point.get("signal_strength")
                        if signal is not None:
                            signal_strengths.append(signal)

            if not signal_strengths:
                return PluginResult(success=False, message="No signal strength data found.")

            avg_strength = sum(signal_strengths) / len(signal_strengths)
            success = avg_strength >= threshold
            message = (
                f"Avg radar signal strength {avg_strength:.2f} meets threshold {threshold:.2f}"
                if success else
                f"Avg radar signal strength {avg_strength:.2f} is below threshold {threshold:.2f}"
            )

            return PluginResult(
                success=success,
                message=message,
                metrics={
                    "radar_signal_quality_score": {
                        "avg": avg_strength,
                        "threshold": threshold
                    }
                }
            )
        except Exception as e:
            return PluginResult(success=False, message=str(e))
