from datetime import datetime
from typing import Any

from app.core.exceptions import NotFoundException
from app.diagnosis.base import DiagnosisContext, DiagnosisResult, DiagnosisType
from app.diagnosis.engine import DiagnosisStrategyFactory
from app.diagnosis.strategies import MotorOverloadContext, MotorOverloadDiagnosisStrategy
from app.models.fault import FaultRule
from app.models.robot import Robot
from app.models.sensor import SensorData
from app.repositories.fault_repository import FaultLogRepository, FaultRuleRepository
from app.repositories.robot_repository import RobotRepository
from app.repositories.sensor_repository import SensorRepository
from app.schemas.diagnosis import (
    DiagnosisReportDTO,
    DiagnosisResultDTO,
    RobotDiagnosisSummaryDTO,
)


class DiagnosisService:
    def __init__(
        self,
        robot_repo: RobotRepository,
        sensor_repo: SensorRepository,
        fault_rule_repo: FaultRuleRepository,
        fault_log_repo: FaultLogRepository,
    ):
        self.robot_repo = robot_repo
        self.sensor_repo = sensor_repo
        self.fault_rule_repo = fault_rule_repo
        self.fault_log_repo = fault_log_repo

    def diagnose_robot(
        self, robot_id: int, diagnosis_types: list[DiagnosisType] | None = None
    ) -> RobotDiagnosisSummaryDTO:
        robot = self.robot_repo.get(robot_id)
        if not robot:
            raise NotFoundException("机器人", robot_id)

        diagnosis_types = diagnosis_types or list(DiagnosisType)
        results: list[DiagnosisResultDTO] = []

        for diag_type in diagnosis_types:
            if diag_type == DiagnosisType.CUSTOM:
                continue

            type_results = self._run_diagnosis_for_type(robot, diag_type)
            results.extend(type_results)

        return RobotDiagnosisSummaryDTO(
            robot_id=robot.id,
            robot_device_id=robot.device_id,
            robot_status=robot.status,
            diagnosis_time=datetime.now(),
            total_checks=len(results),
            triggered_count=sum(1 for r in results if r.triggered),
            results=results,
        )

    def _run_diagnosis_for_type(
        self, robot: Robot, diag_type: DiagnosisType
    ) -> list[DiagnosisResultDTO]:
        results: list[DiagnosisResultDTO] = []

        strategy = DiagnosisStrategyFactory.get_strategy(diag_type)
        if not strategy:
            return results

        rules = self.fault_rule_repo.list_enabled_by_sensor_type(diag_type.value)

        sensor_data_list = self.sensor_repo.list_by_robot_and_type(
            robot.id, diag_type.value, limit=1
        )

        if not sensor_data_list and not rules:
            return results

        latest_sensor_data = sensor_data_list[0] if sensor_data_list else None

        for rule in rules:
            result = self._evaluate_rule(robot, rule, latest_sensor_data, strategy)
            if result:
                results.append(result)

        if not rules and latest_sensor_data:
            default_result = self._create_default_diagnosis(
                robot, diag_type, latest_sensor_data
            )
            if default_result:
                results.append(default_result)

        return results

    def _evaluate_rule(
        self,
        robot: Robot,
        rule: FaultRule,
        sensor_data: SensorData | None,
        strategy: Any,
    ) -> DiagnosisResultDTO | None:
        if sensor_data is None:
            return None

        context = DiagnosisContext(
            robot_id=robot.id,
            sensor_type=rule.sensor_type,
            value=float(sensor_data.value),
        )

        result = strategy.evaluate(context, rule)

        return DiagnosisResultDTO(
            triggered=result.triggered,
            diagnosis_type=strategy.diagnosis_type,
            rule_id=result.rule_id,
            rule_name=result.rule_name,
            fault_type=result.fault_type,
            description=result.description,
            level=result.level,
            extra=result.extra,
        )

    def _create_default_diagnosis(
        self, robot: Robot, diag_type: DiagnosisType, sensor_data: SensorData
    ) -> DiagnosisResultDTO | None:
        return DiagnosisResultDTO(
            triggered=False,
            diagnosis_type=diag_type,
            rule_id=None,
            rule_name=f"{diag_type.value}默认诊断",
            fault_type=None,
            description=f"传感器数据正常，当前值: {sensor_data.value}",
            level="一般",
            extra={"sensor_value": float(sensor_data.value)},
        )

    def diagnose_motor_overload(
        self,
        robot_id: int,
        current_load: float,
        rated_power: float,
        running_time_minutes: float,
        temperature: float | None = None,
    ) -> DiagnosisReportDTO:
        robot = self.robot_repo.get(robot_id)
        if not robot:
            raise NotFoundException("机器人", robot_id)

        motor_context = MotorOverloadContext(
            robot_id=robot_id,
            current_load=current_load,
            rated_power=rated_power,
            running_time_minutes=running_time_minutes,
            temperature=temperature,
        )

        strategy = MotorOverloadDiagnosisStrategy()
        result = strategy.diagnose_motor_status(motor_context, None)

        return DiagnosisReportDTO(
            robot_id=robot_id,
            robot_device_id=robot.device_id,
            diagnosis_type=DiagnosisType.MOTOR_OVERLOAD,
            sensor_value=current_load,
            threshold=rated_power,
            operator=">",
            is_abnormal=result.triggered,
            severity=result.level,
            description=result.description or "电机运行正常",
            recommendation=(
                result.extra.get("recommendations", []) if result.extra else []
            ),
            timestamp=datetime.now(),
        )

    def get_diagnosis_types(self) -> list[dict[str, Any]]:
        supported_types = DiagnosisStrategyFactory.list_supported_types()
        result = []
        for type_code in supported_types:
            try:
                diag_type = DiagnosisType(type_code)
                strategy = DiagnosisStrategyFactory.get_strategy(diag_type)
                result.append(
                    {
                        "type_code": type_code,
                        "diagnosis_type": diag_type,
                        "strategy_name": strategy.__class__.__name__ if strategy else None,
                    }
                )
            except ValueError:
                continue
        return result

    def run_custom_diagnosis(
        self,
        robot_id: int,
        sensor_type: str,
        value: float,
        operator: str,
        threshold: float,
    ) -> DiagnosisResultDTO:
        robot = self.robot_repo.get(robot_id)
        if not robot:
            raise NotFoundException("机器人", robot_id)

        strategy = DiagnosisStrategyFactory.get_strategy_by_sensor_type(sensor_type)

        if not strategy:
            return DiagnosisResultDTO(
                triggered=False,
                diagnosis_type=DiagnosisType.CUSTOM,
                rule_id=None,
                rule_name="自定义诊断",
                fault_type=sensor_type,
                description=f"不支持的传感器类型: {sensor_type}",
                level="一般",
                extra=None,
            )

        context = DiagnosisContext(
            robot_id=robot_id,
            sensor_type=sensor_type,
            value=value,
        )

        class TempRule:
            id = None
            name = f"自定义{sensor_type}诊断"
            operator = operator
            threshold = threshold
            level = "一般"

        result = strategy.evaluate(context, TempRule())

        return DiagnosisResultDTO(
            triggered=result.triggered,
            diagnosis_type=strategy.diagnosis_type,
            rule_id=result.rule_id,
            rule_name=result.rule_name,
            fault_type=result.fault_type,
            description=result.description,
            level=result.level,
            extra=result.extra,
        )

    def batch_diagnose_robots(
        self, robot_ids: list[int]
    ) -> list[RobotDiagnosisSummaryDTO]:
        results = []
        for robot_id in robot_ids:
            try:
                summary = self.diagnose_robot(robot_id)
                results.append(summary)
            except NotFoundException:
                continue
        return results

    def get_robot_diagnosis_history(
        self, robot_id: int, limit: int = 50
    ) -> list[dict[str, Any]]:
        robot = self.robot_repo.get(robot_id)
        if not robot:
            raise NotFoundException("机器人", robot_id)

        fault_logs = self.fault_log_repo.list_by_robot(robot_id, limit)

        return [
            {
                "id": log.id,
                "fault_type": log.fault_type,
                "description": log.description,
                "level": log.level,
                "status": log.status,
                "created_at": log.created_at,
            }
            for log in fault_logs
        ]
