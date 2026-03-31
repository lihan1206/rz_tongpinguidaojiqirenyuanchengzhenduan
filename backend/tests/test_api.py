import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.robot import RobotCreate


class TestRobotAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_auth(self):
        with patch("app.services.deps.get_current_user") as mock:
            mock.return_value = MagicMock(id=1, username="admin", is_active=True)
            yield mock

    @pytest.fixture
    def mock_permission(self):
        with patch("app.services.rbac.require_permission") as mock:
            mock.return_value = MagicMock()
            yield mock

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestSensorAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200


class TestFaultAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
