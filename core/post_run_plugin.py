# core/post_run_plugin.py

from core.plugin_registry import BasePlugin
from pathlib import Path


class PostRunPlugin(BasePlugin):
    """
    Base class for all post-run plugins that require scenario_path validation.
    """

    def __init__(self, config=None):
        super().__init__(config)
    #     self.scenario_path: Path = None
    #
    # def validate_config(self, config):
    #     required = ['scenario_path']
    #     missing = [k for k in required if k not in config]
    #     if missing:
    #         raise ValueError(f"Missing required config: {', '.join(missing)}")
    #
    #     self.scenario_path = Path(self.config['scenario_path'])
    #     if not self.scenario_path.exists():
    #         raise FileNotFoundError(f"Data file not found: {self.scenario_path}")
    #
    #     return True
