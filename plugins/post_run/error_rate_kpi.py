from core.models import PluginResult, TestContext
from core.post_run_plugin import PostRunPlugin
import json
from pathlib import Path


class ErrorRateKPIPlugin(PostRunPlugin):
    def execute(self, context: TestContext) -> PluginResult:
        threshold = self.config.get("error_rate_threshold", 0.001)  # default 0.1%
        error_field = self.config.get("error_rate_field", "error_rate_percent")  # default field
        scenario_path = context.data_path  # TODO pass data_path by Scenario object not by contex

        error_rates = []
        try:
            with open(scenario_path, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    error_rate = entry.get(error_field)
                    if error_rate is not None:
                        error_rates.append(error_rate)
            if not error_rates:
                return PluginResult(success=False, message="No error_rate_percent data found")

            max_error_rate = max(error_rates)
            avg_error_rate = sum(error_rates) / len(error_rates)
            success = max_error_rate <= threshold
            message = (
                f"Max Error rate {max_error_rate:.4%} within threshold {threshold:.4%}"
                if success else
                f"Max Error rate {max_error_rate:.4%} exceeds threshold {threshold:.4%}"
            )

            return PluginResult(
                success=success,
                message=message,
                metrics={
                    "error_rate": {
                        "max": max_error_rate,
                        "avg": avg_error_rate,
                        "threshold": threshold
                    }
                }
            )
        except Exception as e:
            return PluginResult(success=False, message=str(e))
