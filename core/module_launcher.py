import subprocess
import logging
import os

logger = logging.getLogger("ModuleLauncher")

DOCKER_COMPOSE_PATH = "./docker/docker-compose.sut.yaml"  # You can adjust this path
PROJECT_NAME = "sut_modules"

def launch_modules(modules: list):
    """
    Launches specified SUT modules via Docker Compose.
    Each module should match a service name defined in docker-compose.sut.yaml.
    """
    logger.info(f"Launching SUT modules via Docker Compose: {modules}")
    try:
        cmd = ["docker", "compose", "-f", DOCKER_COMPOSE_PATH, "--project-name", PROJECT_NAME, "up", "-d"] + modules
        subprocess.check_call(cmd)
        logger.info(f"Modules launched: {', '.join(modules)}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to launch modules: {e}")
        raise


def stop_modules(modules: list):
    """
    Stops the specified modules via Docker Compose.
    """
    logger.info(f"Stopping SUT modules: {modules}")
    try:
        cmd = ["docker", "compose", "-f", DOCKER_COMPOSE_PATH, "--project-name", PROJECT_NAME, "stop"] + modules
        subprocess.check_call(cmd)
        logger.info("Modules stopped successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to stop modules: {e}")

