from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.auth import Permission, Role, RolePermission, User, UserLog, UserRole
from app.schemas.admin import (
    AdminUserOut,
    AssignPermissionCodesIn,
    AssignRoleCodesIn,
    CreatePermissionIn,
    CreateRoleIn,
    PermissionOut,
    RoleOut,
)
from app.services.deps import get_current_user, get_db
from app.services.rbac import require_permission

router = APIRouter(prefix="/admin", tags=["用户与权限"], dependencies=[Depends(require_permission("config"))])


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Role).order_by(Role.id.asc()).all()


@router.post("/roles", response_model=RoleOut)
def create_role(data: CreateRoleIn, db: Session = Depends(get_db), _=Depends(get_current_user)):
    exists = db.query(Role).filter(Role.code == data.code).first()
    if exists:
        raise HTTPException(status_code=400, detail="角色编码已存在")
    row = Role(code=data.code, name=data.name)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/permissions", response_model=list[PermissionOut])
def list_permissions(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Permission).order_by(Permission.id.asc()).all()


@router.post("/permissions", response_model=PermissionOut)
def create_permission(data: CreatePermissionIn, db: Session = Depends(get_db), _=Depends(get_current_user)):
    exists = db.query(Permission).filter(Permission.code == data.code).first()
    if exists:
        raise HTTPException(status_code=400, detail="权限编码已存在")
    row = Permission(code=data.code, name=data.name)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/roles/{role_id}/permissions")
def set_role_permissions(
    role_id: int,
    data: AssignPermissionCodesIn,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")

    perms = db.query(Permission).filter(Permission.code.in_(data.permission_codes)).all()
    perm_ids = {p.id for p in perms}

    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    for pid in perm_ids:
        db.add(RolePermission(role_id=role_id, permission_id=pid))
    db.commit()

    return {"message": "已更新"}


@router.get("/users", response_model=list[AdminUserOut])
def list_users(db: Session = Depends(get_db), _=Depends(get_current_user)):
    users = db.query(User).order_by(User.id.asc()).all()
    out: list[AdminUserOut] = []

    for u in users:
        role_codes = (
            db.query(Role.code)
            .join(UserRole, UserRole.role_id == Role.id)
            .filter(UserRole.user_id == u.id)
            .all()
        )
        out.append(
            AdminUserOut(
                id=u.id,
                username=u.username,
                full_name=u.full_name,
                phone=u.phone,
                employee_no=u.employee_no,
                is_active=u.is_active,
                roles=[r[0] for r in role_codes],
                created_at=u.created_at,
            )
        )

    return out


@router.put("/users/{user_id}/roles")
def set_user_roles(
    user_id: int,
    data: AssignRoleCodesIn,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    roles = db.query(Role).filter(Role.code.in_(data.role_codes)).all()
    role_ids = {r.id for r in roles}

    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    for rid in role_ids:
        db.add(UserRole(user_id=user_id, role_id=rid))

    db.commit()
    return {"message": "已更新"}


@router.get("/user-logs")
def list_user_logs(limit: int = 200, db: Session = Depends(get_db), _=Depends(get_current_user)):
    rows = db.query(UserLog).order_by(UserLog.id.desc()).limit(min(limit, 500)).all()
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "action": r.action,
            "ip": r.ip,
            "user_agent": r.user_agent,
            "created_at": r.created_at,
        }
        for r in rows
    ]
