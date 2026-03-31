from app.models.fault import AlarmNotification, FaultLog, FaultRule
from app.repositories.fault_repository import AlarmNotificationRepository, FaultLogRepository, FaultRuleRepository
from app.schemas.fault import FaultRuleCreate
from app.services.base import BaseService


class FaultRuleService(BaseService[FaultRule, FaultRuleRepository]):
    def __init__(self, repository: FaultRuleRepository):
        super().__init__(repository)
        self.repository = repository

    def _get_resource_name(self) -> str:
        return "故障规则"

    def list_all(self) -> list[FaultRule]:
        return self.repository.list_all()

    def create(self, data: FaultRuleCreate) -> FaultRule:
        return super().create(data.model_dump())

    def get_enabled_rules_by_sensor_type(self, sensor_type: str) -> list[FaultRule]:
        return self.repository.list_enabled_by_sensor_type(sensor_type)


class FaultLogService(BaseService[FaultLog, FaultLogRepository]):
    def __init__(self, repository: FaultLogRepository):
        super().__init__(repository)
        self.repository = repository

    def _get_resource_name(self) -> str:
        return "故障记录"

    def list_all(self, limit: int = 200) -> list[FaultLog]:
        return self.repository.list_all(limit)

    def update_status(self, log_id: int, status: str) -> FaultLog:
        log = self.repository.update_status(log_id, status)
        if not log:
            from app.core.exceptions import NotFoundException
            raise NotFoundException("故障记录", log_id)
        self.repository.commit()
        return self.repository.refresh(log)

    def create_fault_log(
        self,
        robot_id: int,
        rule_id: int | None,
        fault_type: str,
        description: str,
        level: str,
    ) -> FaultLog:
        log = self.repository.create({
            "robot_id": robot_id,
            "rule_id": rule_id,
            "fault_type": fault_type,
            "description": description,
            "level": level,
        })
        self.repository.commit()
        return self.repository.refresh(log)


class AlarmNotificationService(BaseService[AlarmNotification, AlarmNotificationRepository]):
    def __init__(self, repository: AlarmNotificationRepository):
        super().__init__(repository)
        self.repository = repository

    def _get_resource_name(self) -> str:
        return "告警通知"

    def create_notification(self, fault_log_id: int, channel: str, content: str) -> AlarmNotification:
        notification = self.repository.create_for_fault(fault_log_id, channel, content)
        self.repository.commit()
        return self.repository.refresh(notification)
