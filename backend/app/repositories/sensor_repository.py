from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sensor import Sensor, SensorData
from app.repositories.base import BaseRepository
from app.schemas.sensor import SensorCreate, SensorDataCreate, SensorUpdate


class SensorRepository(BaseRepository[Sensor, SensorCreate, SensorUpdate]):
    """传感器Repository"""

    def __init__(self):
        super().__init__(Sensor)

    def get_by_robot_and_type(
        self,
        db: Session,
        robot_id: int,
        sensor_type: str,
    ) -> Optional[Sensor]:
        """根据机器人ID和传感器类型获取传感器"""
        return self.get_by(db, robot_id=robot_id, sensor_type=sensor_type)

    def list_by_robot(
        self,
        db: Session,
        robot_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Sensor]:
        """获取指定机器人的所有传感器"""
        return self.list(db, robot_id=robot_id, skip=skip, limit=limit)

    def list_by_type(
        self,
        db: Session,
        sensor_type: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Sensor]:
        """按传感器类型获取传感器列表"""
        return self.list(db, sensor_type=sensor_type, skip=skip, limit=limit)

    def update_status(
        self,
        db: Session,
        sensor_id: int,
        status: str,
    ) -> Optional[Sensor]:
        """更新传感器状态"""
        sensor = self.get(db, sensor_id)
        if sensor:
            sensor.status = status
            db.commit()
            db.refresh(sensor)
        return sensor


class SensorDataRepository(BaseRepository[SensorData, SensorDataCreate, None]):
    """传感器数据Repository"""

    def __init__(self):
        super().__init__(SensorData)

    def list_by_sensor(
        self,
        db: Session,
        sensor_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[SensorData]:
        """获取指定传感器的历史数据"""
        query = (
            select(SensorData)
            .filter(SensorData.sensor_id == sensor_id)
            .order_by(SensorData.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        return db.execute(query).scalars().all()

    def get_latest_by_sensor(
        self,
        db: Session,
        sensor_id: int,
    ) -> Optional[SensorData]:
        """获取指定传感器的最新数据"""
        query = (
            select(SensorData)
            .filter(SensorData.sensor_id == sensor_id)
            .order_by(SensorData.timestamp.desc())
            .limit(1)
        )
        return db.execute(query).scalar_one_or_none()

    def get_latest_by_robot_and_type(
        self,
        db: Session,
        robot_id: int,
        sensor_type: str,
    ) -> Optional[SensorData]:
        """获取指定机器人指定类型传感器的最新数据"""
        from app.models.sensor import Sensor

        query = (
            select(SensorData)
            .join(Sensor, SensorData.sensor_id == Sensor.id)
            .filter(Sensor.robot_id == robot_id)
            .filter(Sensor.sensor_type == sensor_type)
            .order_by(SensorData.timestamp.desc())
            .limit(1)
        )
        return db.execute(query).scalar_one_or_none()


# 实例化Repository
sensor_repository = SensorRepository()
sensor_data_repository = SensorDataRepository()