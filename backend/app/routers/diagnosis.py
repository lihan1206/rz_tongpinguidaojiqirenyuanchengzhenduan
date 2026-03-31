from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.diagnosis.base import DiagnosisType
from app.schemas.diagnosis import (
    DiagnosisReportDTO,
    DiagnosisRequestDTO,
    DiagnosisResultDTO,
    DiagnosisTypeInfoDTO,
    RobotDiagnosisSummaryDTO,
)
from app.schemas.fault import ApiResponse
from app.services.container import get_db
from app.services.deps import get_current_user
from app.services.diagnosis_service import DiagnosisService
from app.services.rbac import require_permission

router = APIRouter(prefix="/diagnosis", tags=["诊断服务"])


class MotorOverloadRequest(BaseModel):
    robot_id: Annotated[int, Field(gt=0, description="机器人ID")]
    current_load: Annotated[float, Field(gt=0, description="当前负载(W)")]
    rated_power: Annotated[float, Field(gt=0, description="额定功率(W)")]
    running_time_minutes: Annotated[float, Field(ge=0, description="运行时间(分钟)")]
    temperature: Annotated[float | None, Field(description="电机温度(°C)")] = None


class CustomDiagnosisRequest(BaseModel):
    robot_id: Annotated[int, Field(gt=0, description="机器人ID")]
    sensor_type: Annotated[str, Field(min_length=1, description="传感器类型")]
    value: Annotated[float, Field(description="传感器数值")]
    operator: Annotated[str, Field(description="比较运算符")] = ">"
    threshold: Annotated[float, Field(description="阈值")]


class BatchDiagnosisRequest(BaseModel):
    robot_ids: list[int] = Field(min_length=1, description="机器人ID列表")


def get_diagnosis_service(db: Session = Depends(get_db)) -> DiagnosisService:
    from app.repositories.fault_repository import FaultLogRepository, FaultRuleRepository
    from app.repositories.robot_repository import RobotRepository
    from app.repositories.sensor_repository import SensorRepository

    return DiagnosisService(
        robot_repo=RobotRepository(db),
        sensor_repo=SensorRepository(db),
        fault_rule_repo=FaultRuleRepository(db),
        fault_log_repo=FaultLogRepository(db),
    )


@router.post(
    "/run",
    response_model=RobotDiagnosisSummaryDTO,
    dependencies=[Depends(require_permission("view"))],
    summary="执行机器人诊断",
    description="对指定机器人执行诊断，可选择特定诊断类型或执行全部诊断",
)
def run_diagnosis(
    request: DiagnosisRequestDTO,
    service: DiagnosisService = Depends(get_diagnosis_service),
    _=Depends(get_current_user),
):
    return service.diagnose_robot(request.robot_id, request.diagnosis_types)


@router.get(
    "/run/{robot_id}",
    response_model=RobotDiagnosisSummaryDTO,
    dependencies=[Depends(require_permission("view"))],
    summary="快速执行机器人诊断",
    description="对指定机器人执行全部类型的诊断",
)
def run_diagnosis_quick(
    robot_id: int,
    service: DiagnosisService = Depends(get_diagnosis_service),
    _=Depends(get_current_user),
):
    return service.diagnose_robot(robot_id)


@router.post(
    "/motor-overload",
    response_model=DiagnosisReportDTO,
    dependencies=[Depends(require_permission("view"))],
    summary="电机过载诊断",
    description="对指定机器人的电机进行过载诊断，支持综合评估",
)
def diagnose_motor_overload(
    request: MotorOverloadRequest,
    service: DiagnosisService = Depends(get_diagnosis_service),
    _=Depends(get_current_user),
):
    return service.diagnose_motor_overload(
        robot_id=request.robot_id,
        current_load=request.current_load,
        rated_power=request.rated_power,
        running_time_minutes=request.running_time_minutes,
        temperature=request.temperature,
    )


@router.post(
    "/custom",
    response_model=DiagnosisResultDTO,
    dependencies=[Depends(require_permission("view"))],
    summary="自定义诊断",
    description="使用自定义参数执行诊断",
)
def run_custom_diagnosis(
    request: CustomDiagnosisRequest,
    service: DiagnosisService = Depends(get_diagnosis_service),
    _=Depends(get_current_user),
):
    return service.run_custom_diagnosis(
        robot_id=request.robot_id,
        sensor_type=request.sensor_type,
        value=request.value,
        operator=request.operator,
        threshold=request.threshold,
    )


@router.post(
    "/batch",
    response_model=list[RobotDiagnosisSummaryDTO],
    dependencies=[Depends(require_permission("view"))],
    summary="批量诊断",
    description="对多个机器人执行诊断",
)
def batch_diagnosis(
    request: BatchDiagnosisRequest,
    service: DiagnosisService = Depends(get_diagnosis_service),
    _=Depends(get_current_user),
):
    return service.batch_diagnose_robots(request.robot_ids)


@router.get(
    "/types",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(require_permission("view"))],
    summary="获取支持的诊断类型",
    description="返回系统支持的所有诊断类型及其详细信息",
)
def get_diagnosis_types(
    service: DiagnosisService = Depends(get_diagnosis_service),
    _=Depends(get_current_user),
):
    return DiagnosisTypeInfoDTO.list_all()


@router.get(
    "/history/{robot_id}",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(require_permission("view"))],
    summary="获取诊断历史",
    description="获取指定机器人的诊断历史记录",
)
def get_diagnosis_history(
    robot_id: int,
    limit: Annotated[int, Query(ge=1, le=500, description="返回记录数量")] = 50,
    service: DiagnosisService = Depends(get_diagnosis_service),
    _=Depends(get_current_user),
):
    return service.get_robot_diagnosis_history(robot_id, limit)
