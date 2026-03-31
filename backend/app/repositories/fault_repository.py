from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fault import AlarmNotification, FaultLog, FaultRule
from app.repositories.base import BaseRepository
from app.schemas.fault import FaultLogCreate, FaultRuleCreate, FaultRuleUpdate


class FaultRuleRepository(BaseRepository[FaultRule, FaultRuleCreate, FaultRuleUpdate]):
    """故障规则Repository"""

    def __init__(self):
        super().__init__(FaultRule)

    def list_enabled(
        self,
        db: Session,
        sensor_type: Optional[str] = None,
    ) -> List[FaultRule]:
        """获取所有启用的规则，可按传感器类型过滤"""
        query = select(FaultRule).filter(FaultRule.enabled.is_(True))

        if sensor_type:
            query = query.filter(FaultRule.sensor_type == sensor_type)

        query = query.order_by(FaultRule.level.desc(), FaultRule.id.desc())
        return db.execute(query).scalars().all()

    def get_by_sensor_type_and_name(
        self,
        db: Session,
        sensor_type: str,
        name: str,
    ) -> Optional[FaultRule]:
        """根据传感器类型和名称获取规则"""
        return self.get_by(db, sensor_type=sensor_type, name=name)


class FaultLogRepository(BaseRepository[FaultLog, FaultLogCreate, None]):
    """故障日志Repository"""

    def __init__(self):
        super().__init__(FaultLog)

    def list_by_robot(
        self,
        db: Session,
        robot_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FaultLog]:
        """按机器人ID获取故障日志"""
        query = select(FaultLog).filter(FaultLog.robot_id == robot_id)

        if status:
            query = query.filter(FaultLog.status == status)

        query = query.order_by(FaultLog.created_at.desc()).offset(skip).limit(limit)
        return db.execute(query).scalars().all()

    def count_by_status(
        self,
        db: Session,
        status: Optional[str] = None,
    ) -> int:
        """按状态统计故障数量"""
        query = select(FaultLog)
        if status:
            query = query.filter(FaultLog.status == status)
        return db.execute(query).scalar_one_or_none() or 0

    def update_status(
        self,
        db: Session,
        log_id: int,
        status: str,
    ) -> Optional[FaultLog]:
        """更新故障状态"""
        fault_log = self.get(db, log_id)
        if fault_log:
            fault_log.status = status
            db.commit()
            db.refresh(fault_log)
        return fault_log


class AlarmNotificationRepository(BaseRepository[AlarmNotification, None, None]):
    """告警通知Repository"""

    def __init__(self):
        super().__init__(AlarmNotification)

    def list_by_fault_log(
        self,
        db: Session,
        fault_log_id: int,
    ) -> List[AlarmNotification]:
        """按故障日志获取通知"""
        return self.list(db, fault_log_id=fault_log_id)


# 实例化Repository
fault_rule_repository = FaultRuleRepository()
fault_log_repository = FaultLogRepository()
alarm_notification_repository = AlarmNotificationRepository()