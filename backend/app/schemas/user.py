from datetime import datetime

from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str | None = None


class MeOut(UserOut):
    roles: list[str]
    created_at: datetime
