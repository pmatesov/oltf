# oltf/core/plugin_registry.py

"""
Plugin registry for dynamic plugin discovery and loading
"""

import importlib.util
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Type

from core.models import PluginPhase, TestContext, PluginResult


class BasePlugin:
    """Base class for all plugins - provides standard interface"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = self.__class__.__name__.lower().replace('plugin', '')

    def validate_config(self, config: Dict[str, Any]) -> bool:
        return True

    def execute(self, context: TestContext) -> PluginResult:
        raise NotImplementedError("Plugin must implement 'execute'")


class PluginInfo:
    """Information about a discovered plugin"""

    def __init__(self, name: str, module_path: Path, phase: PluginPhase):
        self.name = name
        self.module_path = module_path
        self.phase = phase
        self.module = None
        self.plugin_class: Optional[Type[BasePlugin]] = None
        self.functions = {}
        self.loaded = False

    def load(self) -> bool:
        try:
            spec = importlib.util.spec_from_file_location(
                f"plugins.{self.phase.value}.{self.name}",
                self.module_path
            )
            if spec is None or spec.loader is None:
                return False

            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)

            self._discover_plugin_interface()

            self.loaded = True
            return True
        except Exception as e:
            logging.error(f"Failed to load plugin {self.name}: {e}")
            return False

    def _discover_plugin_interface(self):
        for name, obj in inspect.getmembers(self.module):
            if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj != BasePlugin:
                self.plugin_class = obj
                return

        # Optional legacy support for function-based plugins
        function_names = ['before_run', 'during_run', 'after_run']
        for func_name in function_names:
            if hasattr(self.module, func_name):
                self.functions[func_name] = getattr(self.module, func_name)


class PluginRegistry:
    """Manages plugin discovery, loading, and execution"""

    def __init__(self, plugins_dir: Path = None):
        self.plugins_dir = plugins_dir or Path('./plugins')
        self.plugins: Dict[PluginPhase, Dict[str, PluginInfo]] = {
            phase: {} for phase in PluginPhase
        }
        self.logger = logging.getLogger('PluginRegistry')

    def discover_plugins(self) -> None:
        if not self.plugins_dir.exists():
            self.logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return

        for phase in PluginPhase:
            phase_dir = self.plugins_dir / phase.value
            if phase_dir.exists():
                self._discover_phase_plugins(phase, phase_dir)

        self.logger.info(f"Discovered {self.total_plugin_count()} plugins")

    def _discover_phase_plugins(self, phase: PluginPhase, phase_dir: Path) -> None:
        for py_file in phase_dir.glob('*.py'):
            if py_file.name.startswith('__'):
                continue
            plugin_name = py_file.stem
            plugin_info = PluginInfo(plugin_name, py_file, phase)
            self.plugins[phase][plugin_name] = plugin_info

    def load_plugins(self, plugin_names: List[str], phase: PluginPhase) -> List[BasePlugin]:
        instances = []
        for name in plugin_names:
            plugin_info = self.plugins[phase].get(name)
            if not plugin_info:
                self.logger.error(f"Plugin not found: {name}")
                continue

            if not plugin_info.loaded and not plugin_info.load():
                self.logger.error(f"Failed to load plugin: {name}")
                continue

            if plugin_info.plugin_class:
                instance = plugin_info.plugin_class()
                instances.append(instance)
            elif plugin_info.functions:
                # Legacy function-based plugin support
                instances.append(plugin_info.functions)
            else:
                self.logger.warning(f"No class or functions found in plugin: {name}")

        return instances

    def get_plugin(self, phase: PluginPhase, plugin_name: str) -> Optional[PluginInfo]:
        return self.plugins[phase].get(plugin_name)

    def execute_plugin(self, phase: PluginPhase, plugin_name: str,
                       context: TestContext,config: Dict[str, Any] = None) -> PluginResult:
        plugin_info = self.get_plugin(phase, plugin_name)
        if not plugin_info:
            return PluginResult(
                success=False,
                message=f"Plugin not found: {plugin_name}",
                plugin_name=plugin_name
            )

        if not plugin_info.loaded and not plugin_info.load():
            return PluginResult(
                success=False,
                message=f"Failed to load plugin: {plugin_name}",
                plugin_name=plugin_name
            )

        try:
            instance = plugin_info.plugin_class(config or {})
            if not instance.validate_config(config or {}):
                return PluginResult(
                    success=False,
                    message=f"Invalid config for plugin: {plugin_name}",
                    plugin_name=plugin_name
                )

            result = instance.execute(context)
            result.plugin_name = plugin_name
            return result
        except Exception as e:
            self.logger.exception(f"Plugin {plugin_name} execution failed: {e}")
            return PluginResult(
                success=False,
                message=f"Exception in plugin: {str(e)}",
                plugin_name=plugin_name
            )

    # def execute_phase_plugins(self, phase: PluginPhase, context: TestContext,
    #                           plugin_configs: Dict[str, Dict[str, Any]] ) -> List[PluginResult]:
    def execute_phase_plugins(self, phase: PluginPhase, context: TestContext,
                              plugin_configs) -> List[PluginResult]:
        results = []
        # for name, cfg in plugin_configs.items():
        for plugin_config in plugin_configs:
            result = self.execute_plugin(phase, plugin_config.get('name'), context, plugin_config.get('config', {}))
            results.append(result)
        return results

    def total_plugin_count(self) -> int:
        return sum(len(p) for p in self.plugins.values())
