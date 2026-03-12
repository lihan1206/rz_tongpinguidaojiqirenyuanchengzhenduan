from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.ticket import MaintenanceTicket, TicketLog
from app.schemas.ticket import TicketCreate, TicketLogOut, TicketOut, TicketUpdate
from app.services.deps import get_current_user, get_db
from app.services.rbac import require_permission

router = APIRouter(prefix="/tickets", tags=["维护工单"])


@router.get("", response_model=list[TicketOut], dependencies=[Depends(require_permission("maintenance"))])
def list_tickets(limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return (
        db.query(MaintenanceTicket)
        .order_by(MaintenanceTicket.id.desc())
        .limit(min(limit, 500))
        .all()
    )


@router.get(
    "/{ticket_id}/logs",
    response_model=list[TicketLogOut],
    dependencies=[Depends(require_permission("maintenance"))],
)
def list_ticket_logs(ticket_id: int, limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return (
        db.query(TicketLog)
        .filter(TicketLog.ticket_id == ticket_id)
        .order_by(TicketLog.id.desc())
        .limit(min(limit, 500))
        .all()
    )


@router.post("", response_model=TicketOut, dependencies=[Depends(require_permission("maintenance"))])
def create_ticket(data: TicketCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = MaintenanceTicket(**data.model_dump())
    db.add(row)
    db.flush()
    db.add(TicketLog(ticket_id=row.id, action="创建", content=row.title))
    db.commit()
    db.refresh(row)
    return row


@router.put("/{ticket_id}", response_model=TicketOut, dependencies=[Depends(require_permission("maintenance"))])
def update_ticket(ticket_id: int, data: TicketUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.get(MaintenanceTicket, ticket_id)
    if not row:
        raise HTTPException(status_code=404, detail="工单不存在")

    before_status = row.status
    before_assignee = row.assignee_user_id

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(row, k, v)

    changes = []
    if data.status is not None and data.status != before_status:
        changes.append(f"状态：{before_status} -> {data.status}")
    if data.assignee_user_id is not None and data.assignee_user_id != before_assignee:
        changes.append(f"指派：{before_assignee} -> {data.assignee_user_id}")

    db.add(TicketLog(ticket_id=row.id, action="更新", content="；".join(changes) if changes else "字段更新"))

    db.commit()
    db.refresh(row)
    return row


@router.delete("/{ticket_id}", dependencies=[Depends(require_permission("maintenance"))])
def delete_ticket(ticket_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.get(MaintenanceTicket, ticket_id)
    if not row:
        raise HTTPException(status_code=404, detail="工单不存在")
    db.add(TicketLog(ticket_id=row.id, action="删除", content=row.title))
    db.delete(row)
    db.commit()
    return {"message": "已删除"}
