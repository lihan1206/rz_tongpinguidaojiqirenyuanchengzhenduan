from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    access_token: str = Field(..., description="访问令牌")
    token_type: str = "Bearer"


class LoginIn(BaseModel):
    account: str = Field(..., description="账号（支持账号/手机号/工号）")
    password: str


class RegisterIn(BaseModel):
    username: str = Field(..., description="账号")
    password: str = Field(..., min_length=6, description="密码")
    full_name: str | None = None
    phone: str | None = None
    employee_no: str | None = None
