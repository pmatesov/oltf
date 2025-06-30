import pytest
from pathlib import Path
from plugins.post_run.data_alignment_jitter_kpi import DataAlignmentJitterKPIPlugin
from tests.utils.test_helpers import create_test_context


@pytest.mark.parametrize("filename, expected_success, expected_max", [
    ("fused_data_with_kpis.jsonl", True, 5),
    ("fused_data_with_kpis.jsonl", False, 2),
])
def test_data_alignment_jitter_kpi(filename, expected_success, expected_max, setup_logger):
    test_dir = Path(__file__).parent
    data_file = test_dir / filename
    context = create_test_context(data_file, setup_logger)

    plugin = DataAlignmentJitterKPIPlugin(config={
        "data_alignment_jitter_threshold": expected_max  # Pass custom threshold to plugin
    })
    plugin.validate_config(plugin.config)
    result = plugin.execute(context)

    assert result.success is expected_success
    assert "data_alignment_jitter_ms" in result.metrics

