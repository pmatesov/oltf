"""
Core data models for the Open Loop Testing Framework
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from enum import Enum
import logging
import time


class TestMode(Enum):
    """Test execution modes"""
    SIL = "SIL"  # Software-in-the-Loop
    HIL = "HIL"  # Hardware-in-the-Loop


class PluginPhase(Enum):
    """Plugin execution phases"""
    BEFORE_RUN = "before_run"
    LIVE = "live"
    POST_RUN = "post_run"

class PluginStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"

@dataclass
class PluginResult:
    """Result from plugin execution"""
    success: bool
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    plugin_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'success': self.success,
            'message': self.message,
            'metrics': self.metrics,
            'duration_ms': self.duration_ms,
            'timestamp': self.timestamp,
            'plugin_name': self.plugin_name
        }


@dataclass
class TestContext:
    """Test execution context passed to plugins"""
    # config: Dict[str, Any]
    scenario_name: str
    data_path: Path
    # output_dir: Path
    # temp_dir: Path
    logger: logging.Logger
    mode: TestMode

    # Runtime state
    metrics: Dict[str, Any] = field(default_factory=dict)
    plugin_results: Dict[str, List[PluginResult]] = field(default_factory=dict)
    system_modules: List[str] = field(default_factory=list)

    def add_metric(self, name: str, value: Any) -> None:
        self.metrics[name] = value

    def get_metric(self, name: str, default: Any = None) -> Any:
        return self.metrics.get(name, default)

    def add_plugin_result(self, phase: str, result: PluginResult) -> None:
        if phase not in self.plugin_results:
            self.plugin_results[phase] = []
        self.plugin_results[phase].append(result)


@dataclass
class KPIThreshold:
    """KPI threshold configuration"""
    name: str
    value: Union[float, int]
    operator: str = "lt"  # lt, gt, eq, lte, gte
    unit: str = ""

    def check(self, actual_value: Union[float, int]) -> bool:
        """Check if actual value meets threshold"""
        ops = {
            "lt": lambda a, b: a < b,
            "gt": lambda a, b: a > b,
            "eq": lambda a, b: a == b,
            "lte": lambda a, b: a <= b,
            "gte": lambda a, b: a >= b
        }
        if self.operator not in ops:
            raise ValueError(f"Unknown operator: {self.operator}")
        return ops[self.operator](actual_value, self.value)


@dataclass
class ScenarioConfig:
    """Test scenario configuration"""
    name: str
    datapath: Path
    plugins: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TestConfiguration:
    """Complete test configuration from YAML"""
    name: str
    mode: TestMode
    scenarios: List[ScenarioConfig]

    before_run_plugins: List[str] = field(default_factory=list)
    live_plugins: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    post_run_plugins: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    sut_modules: List[str] = field(default_factory=list)
    log_config: Dict[str, Any] = field(default_factory=dict)

    output_dir: Path = Path("./reports")
    temp_dir: Path = Path("./tmp")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestConfiguration":
        config_data = data

        scenarios = []
        for scenario_data in config_data.get("scenarios", []):
            plugins = scenario_data.get("plugins", [])
            scenarios.append(ScenarioConfig(
                name=scenario_data.get("name", "Unnamed"),
                datapath=Path(scenario_data.get("datapath")),
                plugins=plugins
            ))

        return cls(
            scenarios=scenarios,
            name=config_data.get("name", "Unnamed Test Run"),
            mode=TestMode(config_data.get("mode", "SIL"))
        )


@dataclass
class TestSummary:
    """Test execution summary"""
    test_name: str
    start_time: float
    end_time: float
    duration_s: float
    total_scenarios: int
    passed_scenarios: int
    failed_scenarios: int
    total_plugins: int
    passed_plugins: int
    failed_plugins: int

    kpi_results: Dict[str, Any] = field(default_factory=dict)
    plugin_results: Dict[str, List[PluginResult]] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        return self.passed_scenarios / self.total_scenarios if self.total_scenarios else 0.0

    @property
    def plugin_success_rate(self) -> float:
        return self.passed_plugins / self.total_plugins if self.total_plugins else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'test_name': self.test_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration_s': self.duration_s,
            'total_scenarios': self.total_scenarios,
            'passed_scenarios': self.passed_scenarios,
            'failed_scenarios': self.failed_scenarios,
            'success_rate': self.success_rate,
            'total_plugins': self.total_plugins,
            'passed_plugins': self.passed_plugins,
            'failed_plugins': self.failed_plugins,
            'plugin_success_rate': self.plugin_success_rate,
            'kpi_results': self.kpi_results,
            'plugin_results': {
                phase: [result.to_dict() for result in results]
                for phase, results in self.plugin_results.items()
            }
        }
