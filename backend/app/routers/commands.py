import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.command import CommandLog, MaintenanceCommand, RemoteCommand
from app.schemas.command import (
    CommandLogOut,
    MaintenanceCommandOut,
    RemoteCommandCreate,
    RemoteCommandOut,
    RemoteCommandUpdate,
)
from app.services.deps import get_current_user, get_db
from app.services.rbac import require_permission

router = APIRouter(prefix="/commands", tags=["远程指令"])


@router.get(
    "/templates",
    response_model=list[MaintenanceCommandOut],
    dependencies=[Depends(require_permission("remote_control"))],
)
def list_templates(db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.query(MaintenanceCommand).order_by(MaintenanceCommand.id.desc()).all()
    return [
        MaintenanceCommandOut(id=r.id, name=r.name, command_type=r.command_type, default_params=r.default_params())
        for r in rows
    ]


@router.get("", response_model=list[RemoteCommandOut], dependencies=[Depends(require_permission("remote_control"))])
def list_commands(limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.query(RemoteCommand).order_by(RemoteCommand.id.desc()).limit(min(limit, 500)).all()
    return [
        RemoteCommandOut(
            id=r.id,
            robot_id=r.robot_id,
            command_type=r.command_type,
            params=r.params(),
            status=r.status,
            result=r.result,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.get(
    "/{command_id}/logs",
    response_model=list[CommandLogOut],
    dependencies=[Depends(require_permission("remote_control"))],
)
def list_command_logs(command_id: int, limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return (
        db.query(CommandLog)
        .filter(CommandLog.remote_command_id == command_id)
        .order_by(CommandLog.id.desc())
        .limit(min(limit, 500))
        .all()
    )


@router.post("", response_model=RemoteCommandOut, dependencies=[Depends(require_permission("remote_control"))])
def create_command(data: RemoteCommandCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = RemoteCommand(
        robot_id=data.robot_id,
        command_type=data.command_type,
        params_json=json.dumps(data.params, ensure_ascii=False),
        status="已下发",
    )
    db.add(row)
    db.flush()
    db.add(CommandLog(remote_command_id=row.id, status=row.status, result=row.result))
    db.commit()
    db.refresh(row)
    return RemoteCommandOut(
        id=row.id,
        robot_id=row.robot_id,
        command_type=row.command_type,
        params=row.params(),
        status=row.status,
        result=row.result,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.put("/{command_id}", response_model=RemoteCommandOut, dependencies=[Depends(require_permission("remote_control"))])
def update_command(command_id: int, data: RemoteCommandUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.get(RemoteCommand, command_id)
    if not row:
        raise HTTPException(status_code=404, detail="指令不存在")

    row.status = data.status
    row.result = data.result
    db.add(CommandLog(remote_command_id=row.id, status=row.status, result=row.result))

    db.commit()
    db.refresh(row)
    return RemoteCommandOut(
        id=row.id,
        robot_id=row.robot_id,
        command_type=row.command_type,
        params=row.params(),
        status=row.status,
        result=row.result,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.delete("/{command_id}", dependencies=[Depends(require_permission("remote_control"))])
def delete_command(command_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    row = db.get(RemoteCommand, command_id)
    if not row:
        raise HTTPException(status_code=404, detail="指令不存在")
    db.delete(row)
    db.commit()
    return {"message": "已删除"}
