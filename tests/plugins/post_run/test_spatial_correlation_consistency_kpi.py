import pytest
from pathlib import Path
from core.models import PluginResult
from plugins.post_run.spatial_correlation_consistency_kpi import SpatialCorrelationConsistencyPlugin
from tests.utils.test_helpers import create_test_context

@pytest.mark.parametrize("filename, expected_success, expected_threshold", [
    ("fused_data_with_kpis.jsonl", True, 0.90),
    ("fused_data_with_kpis.jsonl", False, 0.99),  # higher threshold to force failure
])
def test_spatial_correlation_consistency_kpi(filename, expected_success, expected_threshold, setup_logger):
    test_dir = Path(__file__).parent
    data_file = test_dir / filename
    context = create_test_context(data_file, setup_logger)

    plugin = SpatialCorrelationConsistencyPlugin(config={
        "spatial_correlation_threshold": expected_threshold
    })
    plugin.validate_config(plugin.config)
    result: PluginResult = plugin.execute(context)

    assert result.success is expected_success
    assert "spatial_correlation_score" in result.metrics
    assert "avg" in result.metrics["spatial_correlation_score"]
    if expected_success:
        assert result.metrics["spatial_correlation_score"]["avg"] >= expected_threshold
    else:
        assert result.metrics["spatial_correlation_score"]["avg"] < expected_threshold