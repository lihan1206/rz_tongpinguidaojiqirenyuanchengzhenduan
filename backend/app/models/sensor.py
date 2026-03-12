from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.sql import func

from app.db.base import Base


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), nullable=False)
    sensor_type = Column(String(50), nullable=False)
    value = Column(Numeric(12, 4), nullable=False)
    ts = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
