import pytest
from core.models import PluginResult, TestContext
from plugins.post_run.latency_kpi import LatencyKPIPlugin
from pathlib import Path
from tests.utils.test_helpers import create_test_context


@pytest.mark.parametrize("filename, expected_success, expected_max", [
    ("camera_passing.jsonl", True, 50),
    ("camera_failing.jsonl", False, 50),
])
def test_latency_kpi(filename, expected_success, expected_max, setup_logger):
    test_dir = Path(__file__).parent
    data_file = test_dir / filename
    context: TestContext = create_test_context(data_file, setup_logger)

    # plugin = LatencyKPIPlugin(config={"scenario_path": str(data_file)})
    plugin = LatencyKPIPlugin()
    plugin.validate_config(plugin.config)
    result: PluginResult = plugin.execute(context)

    assert result.success is expected_success
    assert "latency_ms" in result.metrics
    if expected_success:
        assert result.metrics["latency_ms"]["max"] <= expected_max
    else:
        assert result.metrics["latency_ms"]["max"] > expected_max