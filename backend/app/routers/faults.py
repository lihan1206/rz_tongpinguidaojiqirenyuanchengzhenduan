from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.fault import (
    DiagnoseResponse,
    DiagnoseResultItem,
    FaultLogOut,
    FaultRuleCreate,
    FaultRuleOut,
    FaultRuleUpdate,
    FaultStatusUpdate,
)
from app.services.deps import get_current_user, get_db
from app.services.diagnose.diagnose_service import diagnose_service
from app.services.rbac import require_permission

router = APIRouter(prefix="/faults", tags=["故障与告警"])


@router.get(
    "/rules",
    response_model=list[FaultRuleOut],
    dependencies=[Depends(require_permission("diagnose"))],
    summary="获取诊断规则列表",
)
def list_rules(
    sensor_type: Optional[str] = Query(None, description="传感器类型过滤"),
    enabled: Optional[bool] = Query(None, description="是否启用过滤"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """获取诊断规则列表，支持按传感器类型和启用状态过滤"""
    return diagnose_service.list_rules(
        db,
        sensor_type=sensor_type,
        enabled=enabled,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/rules",
    response_model=FaultRuleOut,
    dependencies=[Depends(require_permission("diagnose"))],
    summary="创建诊断规则",
)
def create_rule(
    data: FaultRuleCreate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """创建新的诊断规则"""
    return diagnose_service.create_rule(db, data)


@router.get(
    "/rules/{rule_id}",
    response_model=FaultRuleOut,
    dependencies=[Depends(require_permission("diagnose"))],
    summary="获取单个诊断规则",
)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """获取单个诊断规则详情"""
    return diagnose_service.get_rule(db, rule_id)


@router.put(
    "/rules/{rule_id}",
    response_model=FaultRuleOut,
    dependencies=[Depends(require_permission("diagnose"))],
    summary="更新诊断规则",
)
def update_rule(
    rule_id: int,
    data: FaultRuleUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """更新诊断规则"""
    return diagnose_service.update_rule(db, rule_id, data)


@router.delete(
    "/rules/{rule_id}",
    status_code=204,
    dependencies=[Depends(require_permission("diagnose"))],
    summary="删除诊断规则",
)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """删除诊断规则"""
    diagnose_service.delete_rule(db, rule_id)


@router.post(
    "/diagnose",
    response_model=DiagnoseResponse,
    dependencies=[Depends(require_permission("diagnose"))],
    summary="执行诊断",
)
def execute_diagnose(
    robot_id: int = Query(..., description="机器人ID"),
    sensor_type: Optional[str] = Query(None, description="传感器类型，不指定则诊断所有类型"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """对指定机器人执行故障诊断"""
    if sensor_type:
        results = diagnose_service.execute_diagnose(db, robot_id, sensor_type)
    else:
        results = diagnose_service.execute_diagnose_for_all_types(db, robot_id)

    fault_count = sum(1 for r in results if r.is_fault)

    return DiagnoseResponse(
        robot_id=robot_id,
        results=[DiagnoseResultItem(**r.model_dump()) for r in results],
        fault_count=fault_count,
        executed_at=datetime.now(),
    )


@router.get(
    "/logs",
    response_model=list[FaultLogOut],
    dependencies=[Depends(require_permission("diagnose"))],
    summary="获取故障日志列表",
)
def list_logs(
    robot_id: Optional[int] = Query(None, description="机器人ID过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(200, ge=1, le=1000, description="返回数量限制"),
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """获取故障日志列表，支持按机器人和状态过滤"""
    return diagnose_service.get_fault_logs(
        db,
        robot_id=robot_id,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.put(
    "/logs/{log_id}/status",
    response_model=FaultLogOut,
    dependencies=[Depends(require_permission("diagnose"))],
    summary="更新故障状态",
)
def update_status(
    log_id: int,
    data: FaultStatusUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """更新故障状态（如：未处理、处理中、已解决、已忽略）"""
    return diagnose_service.update_fault_status(db, log_id, data.status)


@router.get(
    "/supported-types",
    response_model=list[str],
    summary="获取支持的诊断类型",
)
def get_supported_types(
    _=Depends(get_current_user),
):
    """获取系统支持的所有诊断类型"""
    return diagnose_service.strategy_factory.get_supported_types()