"""
统一诊断服务
负责收集机器人数据并调用所有诊断策略
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.diagnosis.interfaces import (
    DiagnosisResult,
    DiagnosisSeverity,
    DiagnosisStrategy,
    DiagnosisType,
    RobotDiagnosticData,
)
from app.diagnosis.strategies import (
    TemperatureDiagnosisStrategy,
    PositionDiagnosisStrategy,
    MotorDiagnosisStrategy,
)
from app.models.robot import Robot, RobotPosition
from app.models.sensor import SensorData


@dataclass
class DiagnosticSummary:
    """诊断摘要"""
    robot_id: int
    device_id: str
    overall_status: DiagnosisSeverity
    total_checks: int
    anomaly_count: int
    warning_count: int
    critical_count: int
    results: List[DiagnosisResult]
    timestamp: datetime


class DiagnosisService:
    """
    统一诊断服务
    负责协调所有诊断策略的执行
    """

    def __init__(self, db: Session):
        self.db = db
        self._strategies: Dict[DiagnosisType, DiagnosisStrategy] = {}
        self._register_default_strategies()

    def _register_default_strategies(self):
        """注册默认的诊断策略"""
        self.register_strategy(TemperatureDiagnosisStrategy())
        self.register_strategy(PositionDiagnosisStrategy())
        self.register_strategy(MotorDiagnosisStrategy())

    def register_strategy(self, strategy: DiagnosisStrategy) -> None:
        """
        注册诊断策略

        Args:
            strategy: 诊断策略实例
        """
        self._strategies[strategy.diagnosis_type] = strategy

    def unregister_strategy(self, diagnosis_type: DiagnosisType) -> bool:
        """
        注销诊断策略

        Args:
            diagnosis_type: 诊断类型

        Returns:
            是否成功注销
        """
        if diagnosis_type in self._strategies:
            del self._strategies[diagnosis_type]
            return True
        return False

    def get_strategy(self, diagnosis_type: DiagnosisType) -> Optional[DiagnosisStrategy]:
        """获取指定类型的诊断策略"""
        return self._strategies.get(diagnosis_type)

    def get_all_strategies(self) -> List[DiagnosisStrategy]:
        """获取所有注册的诊断策略"""
        return list(self._strategies.values())

    def get_diagnostic_data(self, robot_id: int) -> Optional[RobotDiagnosticData]:
        """
        获取机器人的诊断数据

        Args:
            robot_id: 机器人ID

        Returns:
            RobotDiagnosticData: 诊断数据对象
        """
        robot = self.db.get(Robot, robot_id)
        if not robot:
            return None

        # 创建诊断数据对象
        diagnostic_data = RobotDiagnosticData(
            robot_id=robot.id,
            device_id=robot.device_id,
            status=robot.status,
            last_update=robot.created_at
        )

        # 获取最新位置数据
        latest_position = (
            self.db.query(RobotPosition)
            .filter(RobotPosition.robot_id == robot_id)
            .order_by(RobotPosition.ts.desc())
            .first()
        )
        if latest_position:
            diagnostic_data.current_lat = float(latest_position.lat)
            diagnostic_data.current_lng = float(latest_position.lng)

        # 获取最近的传感器数据
        sensor_data = self._get_recent_sensor_data(robot_id)
        if sensor_data:
            diagnostic_data.raw_sensor_data = sensor_data

            # 解析传感器数据
            if "temperature" in sensor_data:
                diagnostic_data.temperature = float(sensor_data["temperature"])
            if "temperature_threshold" in sensor_data:
                diagnostic_data.temperature_threshold = float(sensor_data["temperature_threshold"])

            if "motor_current" in sensor_data:
                diagnostic_data.motor_current = float(sensor_data["motor_current"])
            if "motor_rated_current" in sensor_data:
                diagnostic_data.motor_rated_current = float(sensor_data["motor_rated_current"])
            if "motor_load" in sensor_data:
                diagnostic_data.motor_load_percentage = float(sensor_data["motor_load"])
            if "motor_overload_threshold" in sensor_data:
                diagnostic_data.motor_overload_threshold = float(sensor_data["motor_overload_threshold"])

            if "position_expected_lat" in sensor_data:
                diagnostic_data.expected_lat = float(sensor_data["position_expected_lat"])
            if "position_expected_lng" in sensor_data:
                diagnostic_data.expected_lng = float(sensor_data["position_expected_lng"])
            if "position_tolerance" in sensor_data:
                diagnostic_data.position_tolerance = float(sensor_data["position_tolerance"])

        return diagnostic_data

    def _get_recent_sensor_data(self, robot_id: int, minutes: int = 60) -> Dict[str, Any]:
        """
        获取最近的传感器数据

        Args:
            robot_id: 机器人ID
            minutes: 过去多少分钟的数据

        Returns:
            合并后的传感器数据字典
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)

        sensor_records = (
            self.db.query(SensorData)
            .filter(
                and_(
                    SensorData.robot_id == robot_id,
                    SensorData.ts >= cutoff_time
                )
            )
            .order_by(SensorData.ts.desc())
            .all()
        )

        result: Dict[str, Any] = {}

        for record in sensor_records:
            sensor_type = record.sensor_type
            value = float(record.value)

            if sensor_type not in result:
                result[sensor_type] = value

        return result

    def diagnose_robot(
        self,
        robot_id: int,
        diagnosis_types: Optional[List[DiagnosisType]] = None
    ) -> Optional[DiagnosticSummary]:
        """
        对机器人进行完整诊断

        Args:
            robot_id: 机器人ID
            diagnosis_types: 要执行的诊断类型列表，None表示执行所有

        Returns:
            DiagnosticSummary: 诊断摘要
        """
        # 获取诊断数据
        diagnostic_data = self.get_diagnostic_data(robot_id)
        if not diagnostic_data:
            return None

        # 确定要执行的诊断
        if diagnosis_types is None:
            strategies_to_run = self._strategies.values()
        else:
            strategies_to_run = [
                self._strategies[dt]
                for dt in diagnosis_types
                if dt in self._strategies
            ]

        # 执行诊断
        results: List[DiagnosisResult] = []
        for strategy in strategies_to_run:
            result = strategy.diagnose(diagnostic_data)
            results.append(result)

        # 计算诊断摘要
        critical_count = sum(1 for r in results if r.severity == DiagnosisSeverity.CRITICAL)
        warning_count = sum(1 for r in results if r.severity == DiagnosisSeverity.WARNING)
        anomaly_count = sum(1 for r in results if r.is_anomaly)

        # 确定整体状态
        if critical_count > 0:
            overall_status = DiagnosisSeverity.CRITICAL
        elif warning_count > 0:
            overall_status = DiagnosisSeverity.WARNING
        elif anomaly_count > 0:
            overall_status = DiagnosisSeverity.WARNING
        else:
            overall_status = DiagnosisSeverity.NORMAL

        return DiagnosticSummary(
            robot_id=robot_id,
            device_id=diagnostic_data.device_id,
            overall_status=overall_status,
            total_checks=len(results),
            anomaly_count=anomaly_count,
            warning_count=warning_count,
            critical_count=critical_count,
            results=results,
            timestamp=datetime.utcnow()
        )

    def diagnose_single(
        self,
        robot_id: int,
        diagnosis_type: DiagnosisType
    ) -> Optional[DiagnosisResult]:
        """
        对机器人进行单项诊断

        Args:
            robot_id: 机器人ID
            diagnosis_type: 诊断类型

        Returns:
            DiagnosisResult: 诊断结果
        """
        strategy = self._strategies.get(diagnosis_type)
        if not strategy:
            return None

        diagnostic_data = self.get_diagnostic_data(robot_id)
        if not diagnostic_data:
            return None

        return strategy.diagnose(diagnostic_data)

    def list_available_strategies(self) -> List[Dict[str, Any]]:
        """
        列出所有可用的诊断策略

        Returns:
            策略信息列表
        """
        return [
            {
                "type": strategy.diagnosis_type.value,
                "name": strategy.get_name(),
                "description": strategy.get_description()
            }
            for strategy in self._strategies.values()
        ]
