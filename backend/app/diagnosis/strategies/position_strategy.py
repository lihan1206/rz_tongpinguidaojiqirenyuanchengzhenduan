"""
位置偏移诊断策略
检测机器人当前位置与预期位置的偏差
"""

import math
from typing import Dict, Any, Optional, Tuple

from app.diagnosis.interfaces import (
    DiagnosisResult,
    DiagnosisSeverity,
    DiagnosisStrategy,
    DiagnosisType,
    RobotDiagnosticData,
)


class PositionDiagnosisStrategy(DiagnosisStrategy):
    """
    位置偏移诊断策略
    检测机器人当前位置与预期位置的偏差
    """

    # 位置偏移阈值（米）
    WARNING_THRESHOLD = 3.0   # 警告阈值
    CRITICAL_THRESHOLD = 10.0  # 严重阈值

    @property
    def diagnosis_type(self) -> DiagnosisType:
        return DiagnosisType.POSITION

    def diagnose(self, data: RobotDiagnosticData) -> DiagnosisResult:
        """
        执行位置诊断

        诊断逻辑：
        - 偏移 < 3m: 正常
        - 3m <= 偏移 < 10m: 警告
        - 偏移 >= 10m: 严重
        """
        robot_id = data.robot_id

        # 检查必要的位置数据
        if data.current_lat is None or data.current_lng is None:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.NORMAL,
                is_anomaly=False,
                message="无当前位置数据，无法诊断",
                robot_id=robot_id,
                details={"available": False},
                suggestion="请检查GPS/定位模块是否正常工作"
            )

        # 如果没有预期位置，只检查当前位置有效性
        if data.expected_lat is None or data.expected_lng is None:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.NORMAL,
                is_anomaly=False,
                message="无预期位置数据，仅验证当前位置",
                robot_id=robot_id,
                details={
                    "available": True,
                    "current_position": {
                        "lat": float(data.current_lat),
                        "lng": float(data.current_lng)
                    },
                    "expected_position": None,
                    "offset_meters": None
                },
                suggestion="请设置预期位置以启用位置偏移检测"
            )

        # 计算位置偏移距离
        offset_meters = self._calculate_distance(
            (float(data.current_lat), float(data.current_lng)),
            (float(data.expected_lat), float(data.expected_lng))
        )

        details: Dict[str, Any] = {
            "available": True,
            "current_position": {
                "lat": float(data.current_lat),
                "lng": float(data.current_lng)
            },
            "expected_position": {
                "lat": float(data.expected_lat),
                "lng": float(data.expected_lng)
            },
            "offset_meters": round(offset_meters, 2),
            "warning_threshold": self.WARNING_THRESHOLD,
            "critical_threshold": self.CRITICAL_THRESHOLD,
            "position_accuracy": self._assess_accuracy(data)
        }

        # 诊断逻辑
        if offset_meters >= self.CRITICAL_THRESHOLD:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.CRITICAL,
                is_anomaly=True,
                message=f"位置严重偏移！当前位置与预期位置偏差 {offset_meters:.2f} 米",
                robot_id=robot_id,
                details=details,
                suggestion="立即检查！可能原因：1)导航故障 2)被外力移动 3)定位系统故障 4)地图数据错误"
            )
        elif offset_meters >= self.WARNING_THRESHOLD:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.WARNING,
                is_anomaly=True,
                message=f"位置偏移警告！当前位置与预期位置偏差 {offset_meters:.2f} 米",
                robot_id=robot_id,
                details=details,
                suggestion="建议检查位置偏差原因。可能原因：1)定位精度下降 2)轻微滑动 3)路径规划偏差"
            )
        else:
            return DiagnosisResult(
                diagnosis_type=self.diagnosis_type,
                severity=DiagnosisSeverity.NORMAL,
                is_anomaly=False,
                message=f"位置正常，偏差 {offset_meters:.2f} 米",
                robot_id=robot_id,
                details=details,
                suggestion="位置在正常范围内"
            )

    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        使用Haversine公式计算两点间的距离（米）

        Args:
            point1: (纬度, 经度)
            point2: (纬度, 经度)

        Returns:
            距离（米）
        """
        lat1, lon1 = point1
        lat2, lon2 = point2

        # 地球半径（米）
        R = 6371000

        # 转换为弧度
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Haversine公式
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _assess_accuracy(self, data: RobotDiagnosticData) -> str:
        """
        评估定位精度
        """
        raw_data = data.raw_sensor_data

        # 从原始传感器数据中检查定位精度信息
        hdop = raw_data.get("hdop")  # 水平精度因子
        satellites = raw_data.get("satellites")  # 卫星数量
        signal_quality = raw_data.get("signal_quality")

        if hdop is not None:
            if hdop <= 1.0:
                return "excellent"
            elif hdop <= 2.0:
                return "good"
            elif hdop <= 5.0:
                return "moderate"
            else:
                return "poor"

        if satellites is not None:
            if satellites >= 8:
                return "excellent"
            elif satellites >= 5:
                return "good"
            elif satellites >= 3:
                return "moderate"
            else:
                return "poor"

        return "unknown"

    def get_description(self) -> str:
        return "检测机器人当前位置与预期位置的偏差，使用Haversine公式计算精确距离"
