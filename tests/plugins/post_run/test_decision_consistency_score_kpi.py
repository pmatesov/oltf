import pytest
from pathlib import Path
from plugins.post_run.decision_consistency_kpi import DecisionConsistencyScorePlugin
from tests.utils.test_helpers import create_test_context


@pytest.mark.parametrize("filename, expected_success, expected_threshold", [
    ("fused_data_with_kpis.jsonl", True, 0.95),
    ("fused_data_with_kpis.jsonl", False, 0.96),  # higher threshold to force failure
])
def test_decision_consistency_score_kpi(filename, expected_success, expected_threshold, setup_logger):
    test_dir = Path(__file__).parent
    data_file = test_dir / filename
    context = create_test_context(data_file, setup_logger)

    plugin = DecisionConsistencyScorePlugin(config={
        "consistency_threshold": expected_threshold
    })
    plugin.validate_config(plugin.config)
    result = plugin.execute(context)

    assert result.success is expected_success
    assert "decision_consistency_score" in result.metrics
    # #assert result.metrics["decision_consistency_score"]["threshold"] == expected_threshold
    if expected_success:
        assert result.metrics["decision_consistency_score"]["score"] >= expected_threshold
    else:
        assert result.metrics["decision_consistency_score"]["score"] < expected_threshold
