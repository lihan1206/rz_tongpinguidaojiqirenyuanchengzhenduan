import json

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class MaintenanceCommand(Base):
    __tablename__ = "maintenance_commands"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    command_type = Column(String(60), nullable=False)
    default_params_json = Column(Text, nullable=False, default="{}")

    def default_params(self) -> dict:
        try:
            return json.loads(self.default_params_json or "{}")
        except Exception:
            return {}


class RemoteCommand(Base):
    __tablename__ = "remote_commands"

    id = Column(Integer, primary_key=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False)
    command_type = Column(String(60), nullable=False)
    params_json = Column(Text, nullable=False, default="{}")
    status = Column(String(20), nullable=False, default="已下发")
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def params(self) -> dict:
        try:
            return json.loads(self.params_json or "{}")
        except Exception:
            return {}


class CommandLog(Base):
    __tablename__ = "command_logs"

    id = Column(Integer, primary_key=True)
    remote_command_id = Column(Integer, ForeignKey("remote_commands.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
