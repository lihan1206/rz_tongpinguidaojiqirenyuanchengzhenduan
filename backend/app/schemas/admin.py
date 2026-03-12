from datetime import datetime

from pydantic import BaseModel


class RoleOut(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


class PermissionOut(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


class AdminUserOut(BaseModel):
    id: int
    username: str
    full_name: str | None
    phone: str | None
    employee_no: str | None
    is_active: bool
    roles: list[str]
    created_at: datetime


class CreateRoleIn(BaseModel):
    code: str
    name: str


class CreatePermissionIn(BaseModel):
    code: str
    name: str


class AssignRoleCodesIn(BaseModel):
    role_codes: list[str]


class AssignPermissionCodesIn(BaseModel):
    permission_codes: list[str]
