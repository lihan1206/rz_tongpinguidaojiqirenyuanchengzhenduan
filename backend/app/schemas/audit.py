from datetime import datetime

from pydantic import BaseModel


class OperationLogOut(BaseModel):
    id: int
    user_id: int | None
    method: str
    path: str
    summary: str | None
    created_at: datetime

    class Config:
        from_attributes = True
