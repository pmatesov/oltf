import pytest
from pathlib import Path
from core.models import PluginResult
from plugins.post_run.latency_kpi import LatencyKPIPlugin
from tests.utils.test_helpers import create_test_context

@pytest.mark.parametrize("filename, expected_success, expected_max", [
    ("fused_data_with_kpis.jsonl", True, 120),
    ("fused_data_with_kpis.jsonl", False, 80),
])
def test_fusion_latency_kpi(filename, expected_success, expected_max, setup_logger):
    test_dir = Path(__file__).parent
    data_file = test_dir / filename
    context = create_test_context(data_file, setup_logger)

    plugin = LatencyKPIPlugin(config={
        "latency_field": "fusion_latency_ms",
        "latency_threshold": expected_max
    })
    plugin.validate_config(plugin.config)
    result: PluginResult = plugin.execute(context)

    assert result.success is expected_success
    assert "fusion_latency_ms" in result.metrics
    assert "max" in result.metrics["fusion_latency_ms"]
    assert "avg" in result.metrics["fusion_latency_ms"]
    if expected_success:
        assert result.metrics["fusion_latency_ms"]["max"] <= expected_max
    else:
        assert result.metrics["fusion_latency_ms"]["max"] > expected_max
