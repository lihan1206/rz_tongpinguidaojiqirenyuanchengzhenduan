from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.models.auth import User


class Robot(Base):
    __tablename__ = "robots"

    id = Column(Integer, primary_key=True)
    device_id = Column(String(80), unique=True, nullable=False)
    model = Column(String(80), nullable=True)
    location = Column(String(200), nullable=True)
    status = Column(String(30), nullable=False, default="离线")
    ip = Column(String(60), nullable=True)
    port = Column(Integer, nullable=True)
    bound_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    bound_user = relationship("User", primaryjoin="Robot.bound_user_id==User.id", lazy="joined")


class RobotPosition(Base):
    __tablename__ = "robot_positions"

    id = Column(Integer, primary_key=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False)
    lat = Column(Numeric(10, 6), nullable=False)
    lng = Column(Numeric(10, 6), nullable=False)
    ts = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RobotStatusLog(Base):
    __tablename__ = "robot_status_logs"

    id = Column(Integer, primary_key=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False)
    from_status = Column(String(30), nullable=True)
    to_status = Column(String(30), nullable=False)
    ts = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    note = Column(String(200), nullable=True)
