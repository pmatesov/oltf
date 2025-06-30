import pytest
from pathlib import Path
from plugins.post_run.radar_signal_quality_score_kpi import RadarSignalQualityScorePlugin
from tests.utils.test_helpers import create_test_context

@pytest.mark.parametrize("filename, expected_success, threshold", [
    ("radar_data_with_kpis.jsonl", True, 0.8),
    ("radar_data_with_kpis.jsonl", False, 0.95),  # Expected to fail due to high threshold
])
def test_radar_signal_quality_score_kpi(filename, expected_success, threshold, setup_logger):
    test_dir = Path(__file__).parent
    data_file = test_dir / filename
    context = create_test_context(data_file, setup_logger)

    plugin = RadarSignalQualityScorePlugin(config={
        "min_avg_signal_strength": threshold
    })
    plugin.validate_config(plugin.config)
    result = plugin.execute(context)

    assert result.success is expected_success
    assert "radar_signal_quality_score" in result.metrics
    avg_signal = result.metrics["radar_signal_quality_score"]["avg"]

    if expected_success:
        assert avg_signal >= threshold
    else:
        assert avg_signal < threshold
