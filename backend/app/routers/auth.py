from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.models.auth import Role, User, UserLog, UserRole
from app.schemas.auth import LoginIn, RegisterIn, TokenOut
from app.schemas.user import MeOut
from app.services.deps import get_current_user, get_db
from app.services.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["鉴权"])


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, request: Request, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            (User.username == data.account)
            | (User.phone == data.account)
            | (User.employee_no == data.account)
        )
        .first()
    )
    if not user:
        raise HTTPException(status_code=400, detail="账号或密码错误")

    if user.auth_source == "ldap":
        # 可选 LDAP：仅在配置了服务时启用，避免“假实现”
        raise HTTPException(status_code=400, detail="该账号使用LDAP登录，请配置LDAP后再使用")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="账号或密码错误")

    token = create_access_token(str(user.id))

    db.add(
        UserLog(
            user_id=user.id,
            action="登录",
            ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    )
    db.commit()

    return TokenOut(access_token=token)


@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.username == data.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="账号已存在")

    user = User(
        username=data.username,
        full_name=data.full_name,
        phone=data.phone,
        employee_no=data.employee_no,
        auth_source="local",
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.flush()

    # 默认分配普通操作员角色
    operator = db.query(Role).filter(Role.code == "operator").first()
    if operator:
        db.add(UserRole(user_id=user.id, role_id=operator.id))

    db.commit()
    return {"message": "注册成功"}


@router.get("/me", response_model=MeOut)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    role_names = (
        db.query(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == current_user.id)
        .all()
    )
    roles = [r[0] for r in role_names]
    return MeOut(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        roles=roles,
        created_at=current_user.created_at,
    )
