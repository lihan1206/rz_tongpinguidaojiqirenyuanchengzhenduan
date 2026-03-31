import importlib
import inspect
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Type

logger = logging.getLogger(__name__)


class PluginInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    def initialize(self, config: dict[str, Any] | None = None) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass


class DiagnosisPluginInterface(PluginInterface):
    @property
    @abstractmethod
    def sensor_types(self) -> list[str]:
        pass

    @abstractmethod
    def get_strategy_class(self) -> type:
        pass


class NotificationPluginInterface(PluginInterface):
    @property
    @abstractmethod
    def channel(self) -> str:
        pass

    @abstractmethod
    def get_strategy_class(self) -> type:
        pass


class PluginManager:
    def __init__(self):
        self._plugins: dict[str, PluginInterface] = {}
        self._plugin_configs: dict[str, dict[str, Any]] = {}

    def register(self, plugin: PluginInterface, config: dict[str, Any] | None = None) -> None:
        self._plugins[plugin.name] = plugin
        self._plugin_configs[plugin.name] = config or {}
        plugin.initialize(config)
        logger.info(f"Plugin registered: {plugin.name} v{plugin.version}")

    def unregister(self, plugin_name: str) -> None:
        if plugin_name in self._plugins:
            self._plugins[plugin_name].shutdown()
            del self._plugins[plugin_name]
            del self._plugin_configs[plugin_name]
            logger.info(f"Plugin unregistered: {plugin_name}")

    def get(self, plugin_name: str) -> PluginInterface | None:
        return self._plugins.get(plugin_name)

    def list_plugins(self) -> list[str]:
        return list(self._plugins.keys())

    def load_from_directory(self, directory: Path, plugin_type: type[PluginInterface]) -> int:
        loaded_count = 0
        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            module_name = file_path.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, plugin_type)
                            and obj != plugin_type
                        ):
                            plugin_instance = obj()
                            self.register(plugin_instance)
                            loaded_count += 1

            except Exception as e:
                logger.exception(f"Failed to load plugin from {file_path}: {e}")

        return loaded_count

    def reload(self, plugin_name: str) -> bool:
        plugin = self.get(plugin_name)
        if plugin:
            config = self._plugin_configs.get(plugin_name, {})
            plugin.shutdown()
            plugin.initialize(config)
            logger.info(f"Plugin reloaded: {plugin_name}")
            return True
        return False


plugin_manager = PluginManager()
