import logging
from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import ErrorCode, BusinessException
from app.models.fault import FaultLog, FaultRule
from app.models.sensor import SensorData
from app.repositories import (
    fault_log_repository,
    fault_rule_repository,
    sensor_data_repository,
    sensor_repository,
)
from app.schemas.fault import (
    FaultLogCreate,
    FaultLogOut,
    FaultRuleCreate,
    FaultRuleOut,
    FaultRuleUpdate,
)
from app.services.diagnose.strategy_factory import strategy_factory
from app.services.diagnose.strategies import DiagnoseResult

logger = logging.getLogger(__name__)


class DiagnoseService:
    """诊断服务类"""

    def __init__(self):
        self.strategy_factory = strategy_factory
        self.fault_rule_repo = fault_rule_repository
        self.fault_log_repo = fault_log_repository
        self.sensor_data_repo = sensor_data_repository
        self.sensor_repo = sensor_repository

    def create_rule(self, db: Session, rule_data: FaultRuleCreate) -> FaultRuleOut:
        """创建诊断规则"""
        # 检查规则是否已存在
        existing = self.fault_rule_repo.get_by_sensor_type_and_name(
            db,
            sensor_type=rule_data.sensor_type,
            name=rule_data.name,
        )
        if existing:
            raise BusinessException(
                error_code=ErrorCode.DIAGNOSE_RULE_ALREADY_EXISTS,
                message=f"该传感器类型下已存在同名规则: {rule_data.name}",
            )

        # 检查是否支持该传感器类型
        if not self.strategy_factory.has_strategy(rule_data.sensor_type):
            raise BusinessException(
                error_code=ErrorCode.DIAGNOSE_TYPE_NOT_SUPPORTED,
                message=f"不支持的传感器类型: {rule_data.sensor_type}",
                detail={"supported_types": self.strategy_factory.get_supported_types()},
            )

        rule = self.fault_rule_repo.create(db, obj_in=rule_data)
        return FaultRuleOut.model_validate(rule)

    def update_rule(
        self,
        db: Session,
        rule_id: int,
        rule_data: FaultRuleUpdate,
    ) -> FaultRuleOut:
        """更新诊断规则"""
        rule = self.fault_rule_repo.get(db, rule_id)
        if not rule:
            raise BusinessException(
                error_code=ErrorCode.DIAGNOSE_RULE_NOT_FOUND,
                message=f"诊断规则不存在: {rule_id}",
            )

        updated_rule = self.fault_rule_repo.update(db, db_obj=rule, obj_in=rule_data)
        return FaultRuleOut.model_validate(updated_rule)

    def delete_rule(self, db: Session, rule_id: int) -> None:
        """删除诊断规则"""
        rule = self.fault_rule_repo.get(db, rule_id)
        if not rule:
            raise BusinessException(
                error_code=ErrorCode.DIAGNOSE_RULE_NOT_FOUND,
                message=f"诊断规则不存在: {rule_id}",
            )
        self.fault_rule_repo.delete(db, id=rule_id)

    def get_rule(self, db: Session, rule_id: int) -> FaultRuleOut:
        """获取单个诊断规则"""
        rule = self.fault_rule_repo.get(db, rule_id)
        if not rule:
            raise BusinessException(
                error_code=ErrorCode.DIAGNOSE_RULE_NOT_FOUND,
                message=f"诊断规则不存在: {rule_id}",
            )
        return FaultRuleOut.model_validate(rule)

    def list_rules(
        self,
        db: Session,
        sensor_type: str | None = None,
        enabled: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FaultRuleOut]:
        """获取诊断规则列表"""
        filters = {}
        if sensor_type is not None:
            filters["sensor_type"] = sensor_type
        if enabled is not None:
            filters["enabled"] = enabled

        rules = self.fault_rule_repo.list(
            db,
            skip=skip,
            limit=limit,
            order_by=FaultRule.level.desc(),
            **filters,
        )
        return [FaultRuleOut.model_validate(rule) for rule in rules]

    def execute_diagnose(
        self,
        db: Session,
        robot_id: int,
        sensor_type: str,
    ) -> List[DiagnoseResult]:
        """执行诊断"""
        # 获取最新的传感器数据
        sensor_data = self.sensor_data_repo.get_latest_by_robot_and_type(
            db,
            robot_id=robot_id,
            sensor_type=sensor_type,
        )

        if not sensor_data:
            raise BusinessException(
                error_code=ErrorCode.SENSOR_DATA_INVALID,
                message=f"机器人 {robot_id} 没有 {sensor_type} 类型的传感器数据",
            )

        # 获取诊断策略
        strategy = self.strategy_factory.get_strategy(sensor_type)

        # 获取启用的诊断规则
        rules = self.fault_rule_repo.list_enabled(db, sensor_type=sensor_type)

        # 执行诊断
        results = strategy.diagnose(sensor_data, rules)

        # 记录故障日志
        self._record_fault_logs(db, robot_id, results)

        return results

    def execute_diagnose_for_all_types(
        self,
        db: Session,
        robot_id: int,
    ) -> List[DiagnoseResult]:
        """对所有支持的传感器类型执行诊断"""
        all_results: List[DiagnoseResult] = []

        for sensor_type in self.strategy_factory.get_supported_types():
            try:
                results = self.execute_diagnose(db, robot_id, sensor_type)
                all_results.extend(results)
            except BusinessException as e:
                logger.warning(f"诊断 {sensor_type} 时跳过: {e.message}")
                continue

        return all_results

    def _record_fault_logs(
        self,
        db: Session,
        robot_id: int,
        results: List[DiagnoseResult],
    ) -> None:
        """记录故障日志"""
        for result in results:
            if result.is_fault:
                fault_log_data = FaultLogCreate(
                    robot_id=robot_id,
                    rule_id=result.rule_id,
                    fault_type=result.fault_type,
                    description=result.description,
                    level=result.level,
                    status="未处理",
                )
                self.fault_log_repo.create(db, obj_in=fault_log_data)

    def get_fault_logs(
        self,
        db: Session,
        robot_id: int | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FaultLogOut]:
        """获取故障日志列表"""
        if robot_id:
            logs = self.fault_log_repo.list_by_robot(
                db,
                robot_id=robot_id,
                status=status,
                skip=skip,
                limit=limit,
            )
        else:
            filters = {}
            if status:
                filters["status"] = status
            logs = self.fault_log_repo.list(
                db,
                skip=skip,
                limit=limit,
                order_by=FaultLog.created_at.desc(),
                **filters,
            )

        return [FaultLogOut.model_validate(log) for log in logs]

    def update_fault_status(
        self,
        db: Session,
        log_id: int,
        status: str,
    ) -> FaultLogOut:
        """更新故障状态"""
        valid_statuses = ["未处理", "处理中", "已解决", "已忽略"]
        if status not in valid_statuses:
            raise BusinessException(
                error_code=ErrorCode.FAULT_STATUS_INVALID,
                message=f"无效的故障状态: {status}",
                detail={"valid_statuses": valid_statuses},
            )

        log = self.fault_log_repo.update_status(db, log_id=log_id, status=status)
        if not log:
            raise BusinessException(
                error_code=ErrorCode.FAULT_LOG_NOT_FOUND,
                message=f"故障记录不存在: {log_id}",
            )

        return FaultLogOut.model_validate(log)


# 创建全局服务实例
diagnose_service = DiagnoseService()