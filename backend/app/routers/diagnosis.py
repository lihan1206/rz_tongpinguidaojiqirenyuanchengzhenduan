"""
诊断相关API路由
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.diagnosis.interfaces import DiagnosisType
from app.diagnosis.service import DiagnosisService
from app.models.diagnosis import DiagnosisRecord
from app.schemas.diagnosis import (
    DiagnosisRecordCreate,
    DiagnosisRecordDTO,
    DiagnosisRequest,
    DiagnosisResponse,
    DiagnosisResultDTO,
    DiagnosticSummaryDTO,
    DiagnosisStrategyInfoDTO,
    DiagnosisConfigDTO,
    DiagnosisConfigUpdate,
)
from app.services.deps import get_current_user
from app.models.auth import User


router = APIRouter(prefix="/diagnosis", tags=["诊断管理"])


@router.post("/robot/{robot_id}", response_model=DiagnosticSummaryDTO)
def diagnose_robot(
    robot_id: int,
    request: Optional[DiagnosisRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    对指定机器人进行完整诊断
    """
    diagnosis_service = DiagnosisService(db)

    # 检查机器人是否存在
    robot = db.query(diagnosis_service._strategies).first()  # noqa
    if not robot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )

    # 解析诊断类型
    diagnosis_types = None
    if request and request.diagnosis_types:
        try:
            diagnosis_types = [DiagnosisType(dt) for dt in request.diagnosis_types]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的诊断类型: {request.diagnosis_types}"
            )

    # 执行诊断
    summary = diagnosis_service.diagnose_robot(robot_id, diagnosis_types)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无法获取机器人诊断数据"
        )

    # 保存诊断记录
    for result in summary.results:
        record = DiagnosisRecord(
            robot_id=robot_id,
            diagnosis_type=result.diagnosis_type.value,
            severity=result.severity.value,
            is_anomaly=result.is_anomaly,
            message=result.message,
            details=result.details,
            suggestion=result.suggestion
        )
        db.add(record)

    db.commit()

    return DiagnosticSummaryDTO(
        robot_id=summary.robot_id,
        device_id=summary.device_id,
        overall_status=summary.overall_status,
        total_checks=summary.total_checks,
        anomaly_count=summary.anomaly_count,
        warning_count=summary.warning_count,
        critical_count=summary.critical_count,
        results=[
            DiagnosisResultDTO(
                diagnosis_type=r.diagnosis_type,
                severity=r.severity,
                is_anomaly=r.is_anomaly,
                message=r.message,
                details=r.details,
                timestamp=r.timestamp,
                robot_id=r.robot_id,
                suggestion=r.suggestion
            )
            for r in summary.results
        ],
        timestamp=summary.timestamp
    )


@router.post("/robot/{robot_id}/single/{diagnosis_type}", response_model=DiagnosisResultDTO)
def diagnose_robot_single(
    robot_id: int,
    diagnosis_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    对指定机器人进行单项诊断
    """
    try:
        diagnosis_type_enum = DiagnosisType(diagnosis_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的诊断类型: {diagnosis_type}"
        )

    diagnosis_service = DiagnosisService(db)
    result = diagnosis_service.diagnose_single(robot_id, diagnosis_type_enum)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="无法获取诊断结果"
        )

    return DiagnosisResultDTO(
        diagnosis_type=result.diagnosis_type,
        severity=result.severity,
        is_anomaly=result.is_anomaly,
        message=result.message,
        details=result.details,
        timestamp=result.timestamp,
        robot_id=result.robot_id,
        suggestion=result.suggestion
    )


@router.get("/strategies", response_model=List[DiagnosisStrategyInfoDTO])
def list_strategies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取所有可用的诊断策略
    """
    diagnosis_service = DiagnosisService(db)
    strategies = diagnosis_service.list_available_strategies()
    return strategies


@router.get("/records/{robot_id}", response_model=List[DiagnosisRecordDTO])
def get_diagnosis_records(
    robot_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取机器人的诊断记录
    """
    records = (
        db.query(DiagnosisRecord)
        .filter(DiagnosisRecord.robot_id == robot_id)
        .order_by(DiagnosisRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return records


@router.get("/records/{robot_id}/latest", response_model=DiagnosticSummaryDTO)
def get_latest_diagnosis(
    robot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
   获取机器人的最新诊断结果
    """
    records = (
        db.query(DiagnosisRecord)
        .filter(DiagnosisRecord.robot_id == robot_id)
        .order_by(DiagnosisRecord.created_at.desc())
        .limit(10)
        .all()
    )

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有诊断记录"
        )

    from app.diagnosis.interfaces import DiagnosisSeverity
    from datetime import datetime

    critical_count = sum(1 for r in records if r.severity == DiagnosisSeverity.CRITICAL.value)
    warning_count = sum(1 for r in records if r.severity == DiagnosisSeverity.WARNING.value)
    anomaly_count = sum(1 for r in records if r.is_anomaly)

    if critical_count > 0:
        overall_status = DiagnosisSeverity.CRITICAL
    elif warning_count > 0:
        overall_status = DiagnosisSeverity.WARNING
    else:
        overall_status = DiagnosisSeverity.NORMAL

    return DiagnosticSummaryDTO(
        robot_id=robot_id,
        device_id="",
        overall_status=overall_status,
        total_checks=len(records),
        anomaly_count=anomaly_count,
        warning_count=warning_count,
        critical_count=critical_count,
        results=[
            DiagnosisResultDTO(
                diagnosis_type=DiagnosisType(r.diagnosis_type),
                severity=DiagnosisSeverity(r.severity),
                is_anomaly=r.is_anomaly,
                message=r.message,
                details=r.details or {},
                timestamp=r.created_at,
                robot_id=r.robot_id,
                suggestion=r.suggestion
            )
            for r in records
        ],
        timestamp=datetime.utcnow()
    )
