from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.auth import Permission, Role, RolePermission, User, UserRole
from app.services.deps import get_current_user, get_db


def get_role_codes(db: Session, user_id: int) -> set[str]:
    rows = (
        db.query(Role.code)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    return {r[0] for r in rows}


def get_permission_codes(db: Session, user_id: int) -> set[str]:
    rows = (
        db.query(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
        .all()
    )
    return {r[0] for r in rows}


def require_permission(permission_code: str) -> Callable:
    def _dep(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> None:
        roles = get_role_codes(db, current_user.id)
        if "admin" in roles:
            return
        perms = get_permission_codes(db, current_user.id)
        if permission_code not in perms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    return _dep
