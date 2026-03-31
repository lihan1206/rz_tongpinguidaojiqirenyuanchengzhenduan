from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable


class ConfigScope(str, Enum):
    GLOBAL = "global"
    ROBOT = "robot"
    SENSOR = "sensor"
    USER = "user"


@dataclass
class ConfigEntry:
    key: str
    value: Any
    scope: ConfigScope
    scope_id: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ConfigProvider(ABC):
    @abstractmethod
    def get(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL, scope_id: str | None = None) -> Any:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, scope: ConfigScope = ConfigScope.GLOBAL, scope_id: str | None = None) -> None:
        pass

    @abstractmethod
    def delete(self, key: str, scope: ConfigScope = ConfigScope.GLOBAL, scope_id: str | None = None) -> None:
        pass

    @abstractmethod
    def list_all(self, scope: ConfigScope | None = None) -> list[ConfigEntry]:
        pass


class ConfigChangeCallback:
    def __init__(self, key: str, callback: Callable[[Any, Any], None]):
        self.key = key
        self.callback = callback
