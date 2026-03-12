from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.fault import FaultLog, FaultRule
from app.schemas.fault import FaultLogOut, FaultRuleCreate, FaultRuleOut
from app.services.deps import get_current_user, get_db
from app.services.rbac import require_permission

router = APIRouter(prefix="/faults", tags=["故障与告警"])


@router.get("/rules", response_model=list[FaultRuleOut], dependencies=[Depends(require_permission("diagnose"))])
def list_rules(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(FaultRule).order_by(FaultRule.id.desc()).all()


@router.post("/rules", response_model=FaultRuleOut, dependencies=[Depends(require_permission("diagnose"))])
def create_rule(data: FaultRuleCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    rule = FaultRule(**data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/logs", response_model=list[FaultLogOut], dependencies=[Depends(require_permission("diagnose"))])
def list_logs(limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(FaultLog).order_by(FaultLog.id.desc()).limit(min(limit, 500)).all()


@router.put("/logs/{log_id}/status", response_model=FaultLogOut, dependencies=[Depends(require_permission("diagnose"))])
def update_status(log_id: int, status: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.get(FaultLog, log_id)
    if not row:
        raise HTTPException(status_code=404, detail="故障记录不存在")
    row.status = status
    db.commit()
    db.refresh(row)
    return row
