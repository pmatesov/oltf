from core.models import PluginResult, TestContext
from core.post_run_plugin import PostRunPlugin
from pathlib import Path
import json


class DataDropRateKPIPlugin(PostRunPlugin):
    def execute(self, context: TestContext) -> PluginResult:
        threshold = self.config.get("drop_rate_threshold", 0.005)  # default: 0.5%
        timestamp_field = self.config.get("timestamp_field", "timestamp")  # default: 'timestamp'
        expected_interval = self.config.get("expected_interval", 100)  # ms between frames
        scenario_path = context.data_path  # TODO pass data_path by Scenario object not by contex

        timestamps = []
        malformed_lines = 0

        try:
            with open(scenario_path, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        ts = entry.get(timestamp_field)
                        if ts is not None:
                            timestamps.append(int(ts))
                    except json.JSONDecodeError:
                        malformed_lines += 1

            if not timestamps:
                return PluginResult(success=False, message="No valid timestamps found")

            timestamps.sort()
            drops = 0
            for i in range(1, len(timestamps)):
                gap = timestamps[i] - timestamps[i - 1]
                if gap > expected_interval:
                    missing = (gap // expected_interval) - 1
                    drops += missing

            total_expected = drops + len(timestamps)
            drop_rate = (drops + malformed_lines) / total_expected

            success = drop_rate <= threshold
            message = (
                f"Data drop rate {drop_rate:.2%} within threshold {threshold:.2%}"
                if success else
                f"Data drop rate {drop_rate:.2%} exceeds threshold {threshold:.2%}"
            )

            return PluginResult(
                success=success,
                message=message,
                metrics={
                    "data_drop_rate": {
                        "drops": drops,
                        "malformed_lines": malformed_lines,
                        "total_expected": total_expected,
                        "drop_rate": drop_rate,
                        "threshold": threshold
                    }
                }
            )
        except Exception as e:
            return PluginResult(success=False, message=str(e))
