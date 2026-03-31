from app.core.exceptions import NotFoundException
from app.diagnosis import DiagnosisContext, DiagnosisEngine
from app.models.fault import FaultLog
from app.models.sensor import SensorData
from app.repositories.fault_repository import AlarmNotificationRepository, FaultLogRepository, FaultRuleRepository
from app.repositories.robot_repository import RobotRepository
from app.repositories.sensor_repository import SensorRepository
from app.schemas.sensor import SensorIn


class SensorService:
    def __init__(
        self,
        sensor_repo: SensorRepository,
        robot_repo: RobotRepository,
        fault_rule_repo: FaultRuleRepository,
        fault_log_repo: FaultLogRepository,
        alarm_repo: AlarmNotificationRepository,
    ):
        self.sensor_repo = sensor_repo
        self.robot_repo = robot_repo
        self.fault_rule_repo = fault_rule_repo
        self.fault_log_repo = fault_log_repo
        self.alarm_repo = alarm_repo
        self.diagnosis_engine = DiagnosisEngine()

    def ingest(self, data: SensorIn) -> SensorData:
        robot = self.robot_repo.get(data.robot_id)
        if not robot:
            raise NotFoundException("机器人", data.robot_id)

        sensor_data = self.sensor_repo.create({
            "robot_id": data.robot_id,
            "sensor_type": data.sensor_type,
            "value": data.value,
        })

        rules = self.fault_rule_repo.list_enabled_by_sensor_type(data.sensor_type)
        context = DiagnosisContext(
            robot_id=data.robot_id,
            sensor_type=data.sensor_type,
            value=float(data.value),
        )

        for rule in rules:
            result = self.diagnosis_engine.diagnose_single(context, rule)
            if result.triggered:
                fault_log = self.fault_log_repo.create({
                    "robot_id": data.robot_id,
                    "rule_id": rule.id,
                    "fault_type": result.fault_type or rule.name,
                    "description": result.description or "",
                    "level": result.level,
                })
                self.alarm_repo.create_for_fault(
                    fault_log_id=fault_log.id,
                    channel="系统",
                    content=f"机器人#{data.robot_id}触发告警：{result.description}",
                )

        self.sensor_repo.commit()
        return self.sensor_repo.refresh(sensor_data)

    def list_data(self, robot_id: int | None = None, limit: int = 200) -> list[SensorData]:
        return self.sensor_repo.list_all(robot_id, limit)
