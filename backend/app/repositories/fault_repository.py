from sqlalchemy.orm import Session

from app.models.fault import AlarmNotification, FaultLog, FaultRule
from app.repositories.base import BaseRepository


class FaultRuleRepository(BaseRepository[FaultRule]):
    def __init__(self, db: Session):
        super().__init__(db, FaultRule)

    def list_all(self) -> list[FaultRule]:
        return self.db.query(FaultRule).order_by(FaultRule.id.desc()).all()

    def list_enabled_by_sensor_type(self, sensor_type: str) -> list[FaultRule]:
        return (
            self.db.query(FaultRule)
            .filter(FaultRule.enabled.is_(True), FaultRule.sensor_type == sensor_type)
            .all()
        )


class FaultLogRepository(BaseRepository[FaultLog]):
    def __init__(self, db: Session):
        super().__init__(db, FaultLog)

    def list_all(self, limit: int = 200) -> list[FaultLog]:
        return self.db.query(FaultLog).order_by(FaultLog.id.desc()).limit(min(limit, 500)).all()

    def update_status(self, log_id: int, status: str) -> FaultLog | None:
        log = self.get(log_id)
        if log:
            log.status = status
            self.db.flush()
        return log


class AlarmNotificationRepository(BaseRepository[AlarmNotification]):
    def __init__(self, db: Session):
        super().__init__(db, AlarmNotification)

    def create_for_fault(self, fault_log_id: int, channel: str, content: str) -> AlarmNotification:
        notification = AlarmNotification(
            fault_log_id=fault_log_id,
            channel=channel,
            content=content,
        )
        self.db.add(notification)
        self.db.flush()
        return notification
