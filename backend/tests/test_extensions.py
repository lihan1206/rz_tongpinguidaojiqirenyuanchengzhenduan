import pytest

from app.plugins import (
    PluginManager,
    plugin_manager,
    CustomDiagnosisPlugin,
    DiagnosisPluginInterface,
)
from app.config import (
    ConfigManager,
    ConfigScope,
    InMemoryConfigProvider,
)


class TestPluginManager:
    @pytest.fixture
    def manager(self):
        return PluginManager()

    def test_register_plugin(self, manager):
        plugin = CustomDiagnosisPlugin()
        manager.register(plugin)

        assert "custom_diagnosis" in manager.list_plugins()
        assert manager.get("custom_diagnosis") == plugin

    def test_unregister_plugin(self, manager):
        plugin = CustomDiagnosisPlugin()
        manager.register(plugin)
        manager.unregister("custom_diagnosis")

        assert "custom_diagnosis" not in manager.list_plugins()

    def test_plugin_initialization(self, manager):
        plugin = CustomDiagnosisPlugin()
        manager.register(plugin, {"test": "config"})

        assert plugin.name == "custom_diagnosis"
        assert plugin.version == "1.0.0"
        assert "custom" in plugin.sensor_types


class TestDiagnosisPlugin:
    def test_plugin_interface(self):
        plugin = CustomDiagnosisPlugin()
        plugin.initialize()

        assert isinstance(plugin, DiagnosisPluginInterface)
        strategy_class = plugin.get_strategy_class()
        assert strategy_class is not None


class TestConfigManager:
    @pytest.fixture
    def config(self):
        return ConfigManager(InMemoryConfigProvider())

    def test_set_and_get(self, config):
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"

    def test_get_with_default(self, config):
        assert config.get("nonexistent", "default") == "default"

    def test_defaults(self, config):
        config.set_defaults({"default_key": "default_value"})
        assert config.get("default_key") == "default_value"

    def test_robot_config(self, config):
        config.set_robot_config(1, "threshold", 80)
        assert config.get_robot_config(1, "threshold") == 80

    def test_sensor_config(self, config):
        config.set_sensor_config("temperature", "unit", "celsius")
        assert config.get_sensor_config("temperature", "unit") == "celsius"

    def test_config_scopes(self, config):
        config.set("global_key", "global_value", ConfigScope.GLOBAL)
        config.set("robot_key", "robot_value", ConfigScope.ROBOT, "1")

        assert config.get("global_key") == "global_value"
        assert config.get("robot_key", scope=ConfigScope.ROBOT, scope_id="1") == "robot_value"

    def test_delete(self, config):
        config.set("delete_key", "value")
        config.delete("delete_key")
        assert config.get("delete_key") is None

    def test_change_callback(self, config):
        changes = []

        def on_change(old, new):
            changes.append((old, new))

        config.on_change("watched_key", on_change)
        config.set("watched_key", "new_value")

        assert len(changes) == 1
        assert changes[0] == (None, "new_value")
