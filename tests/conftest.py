import pytest
import logging

@pytest.fixture
def setup_logger():
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
    return logger
