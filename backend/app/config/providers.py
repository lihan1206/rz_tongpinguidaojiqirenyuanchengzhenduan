import json
import logging
from pathlib import Path
from typing import Any, Callable

from app.config.base import (
    ConfigChangeCallback,
    ConfigEntry,
    ConfigProvider,
    ConfigScope,
)

logger = logging.getLogger(__name__)


class InMemoryConfigProvider(ConfigProvider):
    def __init__(self):
        self._configs: dict[str, ConfigEntry] = {}
        self._callbacks: list[ConfigChangeCallback] = []

    def _make_key(self, key: str, scope: ConfigScope, scope_id: str | None) -> str:
        if scope == ConfigScope.GLOBAL:
            return f"global:{key}"
        return f"{scope.value}:{scope_id}:{key}"

    def get(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL, scope_id: str | None = None) -> Any:
        full_key = self._make_key(key, scope, scope_id)
        entry = self._configs.get(full_key)
        return entry.value if entry else None

    def set(
        self,
        key: str,
        value: Any,
        scope: ConfigScope = ConfigScope.GLOBAL,
        scope_id: str | None = None,
        description: str | None = None,
    ) -> None:
        full_key = self._make_key(key, scope, scope_id)
        old_value = self.get(key, scope, scope_id)

        self._configs[full_key] = ConfigEntry(
            key=key,
            value=value,
            scope=scope,
            scope_id=scope_id,
            description=description,
        )

        self._notify_change(key, old_value, value)

    def delete(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL, scope_id: str | None = None) -> None:
        full_key = self._make_key(key, scope, scope_id)
        if full_key in self._configs:
            del self._configs[full_key]

    def list_all(self, scope: ConfigScope | None = None) -> list[ConfigEntry]:
        if scope is None:
            return list(self._configs.values())
        return [e for e in self._configs.values() if e.scope == scope]

    def on_change(self, key: str, callback: Callable[[Any, Any], None]) -> None:
        self._callbacks.append(ConfigChangeCallback(key, callback))

    def _notify_change(self, key: str, old_value: Any, new_value: Any) -> None:
        for cb in self._callbacks:
            if cb.key == key or cb.key == "*":
                try:
                    cb.callback(old_value, new_value)
                except Exception as e:
                    logger.exception(f"Config callback error: {e}")


class FileConfigProvider(ConfigProvider):
    def __init__(self, file_path: Path):
        self._file_path = file_path
        self._configs: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self._file_path.exists():
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    self._configs = json.load(f)
            except Exception as e:
                logger.exception(f"Failed to load config file: {e}")
                self._configs = {}

    def _save(self) -> None:
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(self._configs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.exception(f"Failed to save config file: {e}")

    def get(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL, scope_id: str | None = None) -> Any:
        full_key = f"{scope.value}:{scope_id}:{key}" if scope_id else f"{scope.value}:{key}"
        return self._configs.get(full_key)

    def set(self, key: str, value: Any, scope: ConfigScope = ConfigScope.GLOBAL, scope_id: str | None = None) -> None:
        full_key = f"{scope.value}:{scope_id}:{key}" if scope_id else f"{scope.value}:{key}"
        self._configs[full_key] = value
        self._save()

    def delete(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL, scope_id: str | None = None) -> None:
        full_key = f"{scope.value}:{scope_id}:{key}" if scope_id else f"{scope.value}:{key}"
        if full_key in self._configs:
            del self._configs[full_key]
            self._save()

    def list_all(self, scope: ConfigScope | None = None) -> list[ConfigEntry]:
        entries = []
        for full_key, value in self._configs.items():
            parts = full_key.split(":")
            if len(parts) >= 2:
                entry_scope = ConfigScope(parts[0])
                if scope is None or entry_scope == scope:
                    entries.append(
                        ConfigEntry(
                            key=parts[-1],
                            value=value,
                            scope=entry_scope,
                            scope_id=parts[1] if len(parts) > 2 else None,
                        )
                    )
        return entries


class ConfigManager:
    def __init__(self, provider: ConfigProvider | None = None):
        self._provider = provider or InMemoryConfigProvider()
        self._defaults: dict[str, Any] = {}

    def set_defaults(self, defaults: dict[str, Any]) -> None:
        self._defaults.update(defaults)

    def get(
        self,
        key: str,
        default: Any = None,
        scope: ConfigScope = ConfigScope.GLOBAL,
        scope_id: str | None = None,
    ) -> Any:
        value = self._provider.get(key, scope, scope_id)
        if value is None:
            return self._defaults.get(key, default)
        return value

    def set(self, key: str, value: Any, scope: ConfigScope = ConfigScope.GLOBAL, scope_id: str | None = None) -> None:
        self._provider.set(key, value, scope, scope_id)

    def delete(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL, scope_id: str | None = None) -> None:
        self._provider.delete(key, scope, scope_id)

    def get_robot_config(self, robot_id: int, key: str, default: Any = None) -> Any:
        return self.get(key, default, ConfigScope.ROBOT, str(robot_id))

    def set_robot_config(self, robot_id: int, key: str, value: Any) -> None:
        self.set(key, value, ConfigScope.ROBOT, str(robot_id))

    def get_sensor_config(self, sensor_type: str, key: str, default: Any = None) -> Any:
        return self.get(key, default, ConfigScope.SENSOR, sensor_type)

    def set_sensor_config(self, sensor_type: str, key: str, value: Any) -> None:
        self.set(key, value, ConfigScope.SENSOR, sensor_type)

    def on_change(self, key: str, callback: Callable[[Any, Any], None]) -> None:
        if isinstance(self._provider, InMemoryConfigProvider):
            self._provider.on_change(key, callback)


config_manager = ConfigManager(InMemoryConfigProvider())

config_manager.set_defaults({
    "diagnosis.enabled": True,
    "notification.default_channels": ["system"],
    "alarm.auto_acknowledge_timeout": 300,
    "sensor.data_retention_days": 30,
    "robot.heartbeat_interval": 60,
})
