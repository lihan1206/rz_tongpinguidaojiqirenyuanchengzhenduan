from typing import Any

from sqlalchemy.orm import Session

from app.models.robot import Robot, RobotPosition, RobotStatusLog
from app.repositories.base import BaseRepository


class RobotRepository(BaseRepository[Robot]):
    def __init__(self, db: Session):
        super().__init__(db, Robot)

    def get_by_device_id(self, device_id: str) -> Robot | None:
        return self.get_by_field("device_id", device_id)

    def list_all(self) -> list[Robot]:
        return self.db.query(Robot).order_by(Robot.id.desc()).all()

    def create_status_log(self, robot_id: int, from_status: str | None, to_status: str, note: str | None = None) -> RobotStatusLog:
        log = RobotStatusLog(
            robot_id=robot_id,
            from_status=from_status,
            to_status=to_status,
            note=note,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def create_position(self, robot_id: int, lat: float, lng: float) -> RobotPosition:
        position = RobotPosition(robot_id=robot_id, lat=lat, lng=lng)
        self.db.add(position)
        self.db.flush()
        return position

    def list_positions(self, robot_id: int, limit: int = 200) -> list[RobotPosition]:
        return (
            self.db.query(RobotPosition)
            .filter(RobotPosition.robot_id == robot_id)
            .order_by(RobotPosition.id.desc())
            .limit(min(limit, 500))
            .all()
        )

    def list_status_logs(self, robot_id: int, limit: int = 200) -> list[RobotStatusLog]:
        return (
            self.db.query(RobotStatusLog)
            .filter(RobotStatusLog.robot_id == robot_id)
            .order_by(RobotStatusLog.id.desc())
            .limit(min(limit, 500))
            .all()
        )


class RobotPositionRepository(BaseRepository[RobotPosition]):
    def __init__(self, db: Session):
        super().__init__(db, RobotPosition)


class RobotStatusLogRepository(BaseRepository[RobotStatusLog]):
    def __init__(self, db: Session):
        super().__init__(db, RobotStatusLog)
