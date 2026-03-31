from app.plugins.base import (
    DiagnosisPluginInterface,
    NotificationPluginInterface,
    PluginInterface,
    PluginManager,
    plugin_manager,
)
from app.plugins.diagnosis_plugins import CustomDiagnosisPlugin, ExampleTemperaturePlugin
from app.plugins.notification_plugins import SlackNotificationPlugin

__all__ = [
    "PluginInterface",
    "DiagnosisPluginInterface",
    "NotificationPluginInterface",
    "PluginManager",
    "plugin_manager",
    "CustomDiagnosisPlugin",
    "ExampleTemperaturePlugin",
    "SlackNotificationPlugin",
]
