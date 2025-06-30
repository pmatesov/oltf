import logging
import os
from datetime import datetime

class LoggerManager:
    base_log_dir = None
    kpi_results = []

    @staticmethod
    def init(config: dict):
        """
        Initialize global logging system.
        """
        level = getattr(logging, config.get("level", "INFO").upper(), logging.INFO)
        LoggerManager.base_log_dir = config.get("local_path", "./reports/logs")
        os.makedirs(LoggerManager.base_log_dir, exist_ok=True)

        log_filename = os.path.join(LoggerManager.base_log_dir, f"test.log")
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )

        logging.getLogger("LoggerManager").info(f"Logging initialized. Logs saved to {log_filename}")

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a named logger (optionally with per-plugin file handler in future).
        """
        return logging.getLogger(name)

    @staticmethod
    def save_kpi_result(plugin_name: str, scenario_name: str, result: dict):
        """
        Accumulate KPI results in memory.
        """
        LoggerManager.kpi_results.append({
            "timestamp": datetime.utcnow().isoformat(),
            "plugin": plugin_name,
            "scenario": scenario_name,
            "result": result
        })

    @staticmethod
    def write_kpi_results_to_json(output_path=None):
        """
        Save all accumulated KPI results to disk.
        """
        import json

        output_path = output_path or os.path.join(LoggerManager.base_log_dir, "kpi_results.json")
        try:
            with open(output_path, "w") as f:
                json.dump(LoggerManager.kpi_results, f, indent=2)
            logging.getLogger("LoggerManager").info(f"KPI results saved to {output_path}")
        except Exception as e:
            logging.getLogger("LoggerManager").error(f"Failed to write KPI results: {e}")

