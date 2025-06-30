from plugins.post_run.latency_kpi import LatencyKPIPlugin
from core.models import TestContext, PluginResult


class DataAlignmentJitterKPIPlugin(LatencyKPIPlugin):
    def execute(self, context: TestContext) -> PluginResult:
        # Fetch values from config with defaults
        jitter_threshold = self.config.get("data_alignment_jitter_threshold", 5.0)
        jitter_field = self.config.get("data_alignment_jitter_field", "data_alignment_jitter_ms")

        # Reuse LatencyKPIPlugin with adjusted field and threshold
        reused_config = {
            **self.config,
            "latency_threshold": jitter_threshold,
            "latency_field": jitter_field
        }

        plugin = LatencyKPIPlugin(config=reused_config)
        plugin.validate_config(plugin.config)
        return plugin.execute(context)
