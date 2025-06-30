import yaml
import logging
from pathlib import Path
from typing import Dict, Any
from core.logger_manager import LoggerManager
from core.plugin_registry import PluginRegistry
from core.models import TestConfiguration, TestContext, PluginResult, PluginPhase, ScenarioConfig
from dashboards.report_generator import generate_html_report


class TestOrchestrator:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            raw_config = yaml.safe_load(f)

        self.config = TestConfiguration.from_dict(raw_config)
        self.logger = LoggerManager.get_logger("TestOrchestrator")
        self.plugin_registry = PluginRegistry()
        self.plugin_registry.discover_plugins()
        self.results = {}

    def run(self):
        self.logger.info(f"Starting test: {self.config.name}")
        for scenario in self.config.scenarios:
            self.logger.info(f"Running scenario: {scenario.name}")

            # New context contains just the scenario name and mode
            context = TestContext(
                scenario_name=scenario.name,
                data_path=scenario.datapath,
                logger=self.logger,
                mode=self.config.mode,
            )

            # BEFORE RUN PHASE
            pass
            # Launch SUT modules
            pass
            # LIVE PHASE
            pass
            # Stopping SUT modules

            # POST RUN PHASE
            self.logger.info("Executing post_run plugins")
            scenario_results = self.plugin_registry.execute_phase_plugins(
                PluginPhase.POST_RUN, context, scenario.plugins
            )

            self.results[scenario.name] = scenario_results
            self.logger.info(f"Scenario {scenario.name} completed")

        self.logger.info("All test scenarios completed.")
        output_path = Path("reports/dashboards/regression_dashboard.html")
        generate_html_report(self.results, output_path)


if __name__ == "__main__":
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else "configs/regression.yaml"
    config_path = Path(config_path).resolve()
    orchestrator = TestOrchestrator(str(config_path))
    orchestrator.run()
