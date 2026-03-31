from sqlalchemy.orm import Session

from app.models.sensor import SensorData
from app.repositories.base import BaseRepository


class SensorRepository(BaseRepository[SensorData]):
    def __init__(self, db: Session):
        super().__init__(db, SensorData)

    def list_by_robot(self, robot_id: int, limit: int = 200) -> list[SensorData]:
        return (
            self.db.query(SensorData)
            .filter(SensorData.robot_id == robot_id)
            .order_by(SensorData.id.desc())
            .limit(min(limit, 500))
            .all()
        )

    def list_all(self, robot_id: int | None = None, limit: int = 200) -> list[SensorData]:
        query = self.db.query(SensorData).order_by(SensorData.id.desc())
        if robot_id is not None:
            query = query.filter(SensorData.robot_id == robot_id)
        return query.limit(min(limit, 500)).all()

    def list_by_robot_and_type(
        self, robot_id: int, sensor_type: str, limit: int = 100
    ) -> list[SensorData]:
        return (
            self.db.query(SensorData)
            .filter(SensorData.robot_id == robot_id, SensorData.sensor_type == sensor_type)
            .order_by(SensorData.id.desc())
            .limit(min(limit, 500))
            .all()
        )

    def get_latest_by_robot_and_type(
        self, robot_id: int, sensor_type: str
    ) -> SensorData | None:
        return (
            self.db.query(SensorData)
            .filter(SensorData.robot_id == robot_id, SensorData.sensor_type == sensor_type)
            .order_by(SensorData.id.desc())
            .first()
        )
