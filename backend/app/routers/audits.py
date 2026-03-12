from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.audit import OperationLog
from app.schemas.audit import OperationLogOut
from app.services.deps import get_current_user, get_db
from app.services.rbac import require_permission

router = APIRouter(prefix="/audits", tags=["审计"])


@router.get("/operations", response_model=list[OperationLogOut], dependencies=[Depends(require_permission("audit"))])
def list_operations(limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(OperationLog).order_by(OperationLog.id.desc()).limit(min(limit, 500)).all()
