from core.models import PluginResult, TestContext
from core.post_run_plugin import PostRunPlugin
import json
from pathlib import Path


class LatencyKPIPlugin(PostRunPlugin):
    def execute(self, context: TestContext) -> PluginResult:
        threshold = self.config.get("latency_threshold", 50.0)  # default 50 ms
        latency_field = self.config.get("latency_field", "latency_ms")  # default latency_ms, could be fusion_latency_ms
        scenario_path = context.data_path  # TODO pass data_path by Scenario object not by contex

        latencies = []
        try:
            with open(scenario_path, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    latency = entry.get(latency_field)
                    if latency is not None:
                        latencies.append(latency)

            if not latencies:
                return PluginResult(success=False, message="No latency data found")

            max_latency = max(latencies)
            avg_latency = sum(latencies) / len(latencies)

            success = max_latency <= threshold
            message = (
                f"Max latency {max_latency:.2f} ms within threshold {threshold} ms"
                if success else
                f"Max latency {max_latency:.2f} ms exceeds threshold {threshold} ms"
            )

            return PluginResult(
                success=success,
                message=message,
                metrics={
                    latency_field: {
                        "max": max_latency,
                        "avg": avg_latency,
                        "threshold": threshold
                    }
                }
            )
        except Exception as e:
            return PluginResult(success=False, message=str(e))
