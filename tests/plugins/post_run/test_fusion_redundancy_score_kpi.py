import pytest
from pathlib import Path
from plugins.post_run.fusion_redundancy_score_kpi import FusionRedundancyScorePlugin
from tests.utils.test_helpers import create_test_context

@pytest.mark.parametrize("filename, expected_success, expected_threshold", [
    ("fused_data_with_kpis.jsonl", True, 0.5),
     ("fused_data_with_kpis.jsonl", False, 0.96),  # artificially high threshold to trigger failure
])
def test_fusion_redundancy_score_kpi(filename, expected_success, expected_threshold, setup_logger):
    test_dir = Path(__file__).parent
    data_file = test_dir / filename
    context = create_test_context(data_file, setup_logger)

    plugin = FusionRedundancyScorePlugin(config={
        "min_redundancy_score": expected_threshold
    })
    plugin.validate_config(plugin.config)
    result = plugin.execute(context)

    assert result.success is expected_success
    assert "fusion_redundancy_score" in result.metrics
    score = result.metrics["fusion_redundancy_score"]["score"]
    if expected_success:
        assert score >= expected_threshold
    else:
        assert score < expected_threshold