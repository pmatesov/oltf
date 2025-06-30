from pathlib import Path
import pytest
from plugins.post_run.error_rate_kpi import ErrorRateKPIPlugin
from core.models import PluginResult
from tests.utils.test_helpers import create_test_context


@pytest.mark.parametrize("filename, expected_success, expected_max", [
    ("camera_passing.jsonl", True, 0.001),
    ("camera_failing.jsonl", False, 0.001),
])
def test_error_rate_kpi(filename, expected_success, expected_max, setup_logger):
    test_dir = Path(__file__).parent
    data_file = test_dir / filename
    context = create_test_context(data_file, setup_logger)

    plugin = ErrorRateKPIPlugin()
    plugin.validate_config(plugin.config)
    result: PluginResult = plugin.execute(context)

    assert result.success is expected_success
    assert "error_rate" in result.metrics
    if expected_success:
        assert result.metrics["error_rate"]["max"] <= expected_max
    else:
        assert result.metrics["error_rate"]["max"] > expected_max
