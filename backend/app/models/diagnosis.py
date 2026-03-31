"""
诊断相关数据库模型
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class DiagnosisRecord(Base):
    """诊断记录表"""
    __tablename__ = "diagnosis_records"

    id = Column(Integer, primary_key=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False)
    diagnosis_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    is_anomaly = Column(Boolean, nullable=False, default=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    robot = relationship("Robot", primaryjoin="DiagnosisRecord.robot_id==Robot.id")


class DiagnosisConfig(Base):
    """诊断配置表 - 用于存储各类型诊断的阈值配置"""
    __tablename__ = "diagnosis_configs"

    id = Column(Integer, primary_key=True)
    diagnosis_type = Column(String(50), unique=True, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    warning_threshold = Column(Numeric(10, 2), nullable=True)
    critical_threshold = Column(Numeric(10, 2), nullable=True)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
