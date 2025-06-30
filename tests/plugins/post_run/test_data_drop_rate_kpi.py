import pytest
from pathlib import Path
from core.models import PluginResult
from plugins.post_run.data_drop_rate_kpi import DataDropRateKPIPlugin
from tests.utils.test_helpers import create_test_context


@pytest.mark.parametrize("filename, expected_success, expected_threshold", [
    ("camera_data_with_kpis.jsonl", False, 0.005),
    ("radar_data_with_kpis.jsonl", True, 0.005),
])
def test_data_drop_rate_kpi(filename, expected_success, expected_threshold, setup_logger):
    test_dir = Path(__file__).parent
    data_file = test_dir / filename
    context = create_test_context(data_file, setup_logger)

    plugin = DataDropRateKPIPlugin(config={
        "expected_interval": 100,  # milliseconds between frames
        "drop_rate_threshold": expected_threshold
    })
    plugin.validate_config(plugin.config)
    result: PluginResult = plugin.execute(context)

    assert result.success is expected_success
    assert "data_drop_rate" in result.metrics
    assert result.metrics["data_drop_rate"]["drop_rate"] <= expected_threshold if expected_success else True
