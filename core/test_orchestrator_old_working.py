import yaml
import logging
import os
from pathlib import Path
from core.logger_manager import LoggerManager
from core.plugin_registry import PluginRegistry
from core.module_launcher import launch_modules, stop_modules
from core.models import TestContext, TestMode, PluginPhase, TestConfiguration


class TestOrchestrator:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            raw_config = yaml.safe_load(f)
        self.config = TestConfiguration.from_dict(raw_config)
        LoggerManager.init(self.config.log_config)

        self.logger = logging.getLogger("TestOrchestrator")
        self.plugin_registry = PluginRegistry()
        self.plugin_registry.discover_plugins()

    def run(self):
        self.logger.info("Starting test: %s", self.config.name)

        for scenario in self.config.scenarios:
            self.logger.info(f"Running scenario: {scenario.name}")

            # prepare paths
            scenario_output = self.config.output_dir / scenario.name
            scenario_output.mkdir(parents=True, exist_ok=True)

            scenario_temp = self.config.temp_dir / scenario.name
            scenario_temp.mkdir(parents=True, exist_ok=True)

            data_paths = {
                key: Path(path) for key, path in scenario.data_files.items()
            }

            context = TestContext(
                config=self.config.__dict__,
                scenario_name=scenario.name,
                data_paths=data_paths,
                output_dir=scenario_output,
                temp_dir=scenario_temp,
                logger=self.logger,
                mode=self.config.mode
            )

            # BEFORE RUN PHASE
            self.logger.info("Executing before_run plugins")
            before_results = self.plugin_registry.execute_phase_plugins(
                PluginPhase.BEFORE_RUN, context, {
                    name: {} for name in self.config.before_run_plugins
                }
            )
            for result in before_results:
                context.add_plugin_result(PluginPhase.BEFORE_RUN.value, result)

            # Launch SUT modules
            if self.config.sut_modules:
                self.logger.info("Launching SUT modules")
                launch_modules(self.config.sut_modules)

            # LIVE PHASE
            self.logger.info("Executing live plugins")
            live_results = self.plugin_registry.execute_phase_plugins(
                PluginPhase.LIVE, context, self.config.live_plugins
            )
            for result in live_results:
                context.add_plugin_result(PluginPhase.LIVE.value, result)

            if self.config.sut_modules:
                self.logger.info("Stopping SUT modules")
                stop_modules(self.config.sut_modules)

            # POST RUN PHASE
            self.logger.info("Executing post_run plugins")
            post_results = self.plugin_registry.execute_phase_plugins(
                PluginPhase.POST_RUN, context, self.config.post_run_plugins
            )
            for result in post_results:
                context.add_plugin_result(PluginPhase.POST_RUN.value, result)

            self.logger.info(f"Scenario {scenario.name} completed")

        self.logger.info("All test scenarios completed.")

if __name__ == "__main__":
    import sys

    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/regression.yaml"
    config_path = Path(config_path).resolve()
    orchestrator = TestOrchestrator(str(config_path))
    orchestrator.run()
