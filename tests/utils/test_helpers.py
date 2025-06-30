import logging
from pathlib import Path
from core.models import TestContext, TestMode


def create_test_context(scenario_file: Path, logger: logging.Logger) -> TestContext:
    return TestContext(
        scenario_name=scenario_file.stem,
        data_path=scenario_file,
        logger=logger,
        mode=TestMode.SIL
    )