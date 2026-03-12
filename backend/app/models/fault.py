from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class FaultRule(Base):
    __tablename__ = "fault_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    sensor_type = Column(String(50), nullable=False)
    operator = Column(String(10), nullable=False, default=">")
    threshold = Column(Integer, nullable=False)
    level = Column(String(20), nullable=False, default="严重")
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class FaultLog(Base):
    __tablename__ = "fault_logs"

    id = Column(Integer, primary_key=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(Integer, ForeignKey("fault_rules.id", ondelete="SET NULL"), nullable=True)
    fault_type = Column(String(60), nullable=False)
    description = Column(Text, nullable=False)
    level = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="未处理")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AlarmNotification(Base):
    __tablename__ = "alarm_notifications"

    id = Column(Integer, primary_key=True)
    fault_log_id = Column(Integer, ForeignKey("fault_logs.id", ondelete="CASCADE"), nullable=False)
    channel = Column(String(30), nullable=False, default="系统")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
