from typing import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.fault_repository import AlarmNotificationRepository, FaultLogRepository, FaultRuleRepository
from app.repositories.robot_repository import RobotRepository
from app.repositories.sensor_repository import SensorRepository
from app.services.fault_service import AlarmNotificationService, FaultLogService, FaultRuleService
from app.services.robot_service import RobotService
from app.services.sensor_service import SensorService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_robot_service(db: Session = None) -> RobotService:
    if db is None:
        db = SessionLocal()
    return RobotService(RobotRepository(db))


def get_fault_rule_service(db: Session = None) -> FaultRuleService:
    if db is None:
        db = SessionLocal()
    return FaultRuleService(FaultRuleRepository(db))


def get_fault_log_service(db: Session = None) -> FaultLogService:
    if db is None:
        db = SessionLocal()
    return FaultLogService(FaultLogRepository(db))


def get_alarm_notification_service(db: Session = None) -> AlarmNotificationService:
    if db is None:
        db = SessionLocal()
    return AlarmNotificationService(AlarmNotificationRepository(db))


def get_sensor_service(db: Session = None) -> SensorService:
    if db is None:
        db = SessionLocal()
    return SensorService(
        sensor_repo=SensorRepository(db),
        robot_repo=RobotRepository(db),
        fault_rule_repo=FaultRuleRepository(db),
        fault_log_repo=FaultLogRepository(db),
        alarm_repo=AlarmNotificationRepository(db),
    )
