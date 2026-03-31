"""
诊断策略模式接口定义
定义诊断策略的抽象基类和数据模型
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DiagnosisSeverity(str, Enum):
    """诊断严重级别"""
    NORMAL = "normal"      # 正常
    WARNING = "warning"    # 警告
    CRITICAL = "critical"  # 严重


class DiagnosisType(str, Enum):
    """诊断类型"""
    TEMPERATURE = "temperature"  # 温度异常
    POSITION = "position"        # 位置偏移
    MOTOR = "motor"              # 电机过载


@dataclass
class DiagnosisResult:
    """诊断结果DTO"""
    diagnosis_type: DiagnosisType
    severity: DiagnosisSeverity
    is_anomaly: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    robot_id: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class RobotDiagnosticData:
    """机器人诊断数据DTO - 用于传递给诊断策略"""
    robot_id: int
    device_id: str
    # 温度数据
    temperature: Optional[float] = None
    temperature_threshold: float = 80.0  # 默认温度阈值
    # 位置数据
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    expected_lat: Optional[float] = None
    expected_lng: Optional[float] = None
    position_tolerance: float = 5.0  # 位置容差（米）
    # 电机数据
    motor_current: Optional[float] = None
    motor_rated_current: Optional[float] = None
    motor_load_percentage: Optional[float] = None
    motor_overload_threshold: float = 90.0  # 电机负载阈值（%）
    # 通用数据
    status: Optional[str] = None
    last_update: Optional[datetime] = None
    raw_sensor_data: Dict[str, Any] = field(default_factory=dict)


class DiagnosisStrategy(ABC):
    """
    诊断策略抽象基类
    所有具体诊断策略必须继承此类
    """

    @property
    @abstractmethod
    def diagnosis_type(self) -> DiagnosisType:
        """返回诊断类型"""
        pass

    @abstractmethod
    def diagnose(self, data: RobotDiagnosticData) -> DiagnosisResult:
        """
        执行诊断

        Args:
            data: 机器人诊断数据

        Returns:
            DiagnosisResult: 诊断结果
        """
        pass

    def get_name(self) -> str:
        """获取策略名称"""
        return self.__class__.__name__

    def get_description(self) -> str:
        """获取策略描述"""
        return f"{self.diagnosis_type.value} diagnosis strategy"
