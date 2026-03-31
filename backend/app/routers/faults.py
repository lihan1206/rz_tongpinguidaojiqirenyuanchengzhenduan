from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.fault import FaultLogOut, FaultLogStatusUpdate, FaultRuleCreate, FaultRuleOut
from app.services.container import get_db, get_fault_log_service, get_fault_rule_service
from app.services.deps import get_current_user
from app.services.fault_service import FaultLogService, FaultRuleService
from app.services.rbac import require_permission

router = APIRouter(prefix="/faults", tags=["故障与告警"])


def get_fault_rule_service_dep(db: Session = Depends(get_db)) -> FaultRuleService:
    return get_fault_rule_service(db)


def get_fault_log_service_dep(db: Session = Depends(get_db)) -> FaultLogService:
    return get_fault_log_service(db)


@router.get("/rules", response_model=list[FaultRuleOut], dependencies=[Depends(require_permission("diagnose"))])
def list_rules(
    service: FaultRuleService = Depends(get_fault_rule_service_dep),
    _=Depends(get_current_user),
):
    return service.list_all()


@router.post("/rules", response_model=FaultRuleOut, dependencies=[Depends(require_permission("diagnose"))])
def create_rule(
    data: FaultRuleCreate,
    service: FaultRuleService = Depends(get_fault_rule_service_dep),
    _=Depends(get_current_user),
):
    return service.create(data)


@router.get("/logs", response_model=list[FaultLogOut], dependencies=[Depends(require_permission("diagnose"))])
def list_logs(
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
    service: FaultLogService = Depends(get_fault_log_service_dep),
    _=Depends(get_current_user),
):
    return service.list_all(limit)


@router.put("/logs/{log_id}/status", response_model=FaultLogOut, dependencies=[Depends(require_permission("diagnose"))])
def update_status(
    log_id: int,
    data: FaultLogStatusUpdate,
    service: FaultLogService = Depends(get_fault_log_service_dep),
    _=Depends(get_current_user),
):
    return service.update_status(log_id, data.status)
