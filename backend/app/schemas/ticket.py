from datetime import datetime

from pydantic import BaseModel


class TicketCreate(BaseModel):
    robot_id: int
    title: str
    description: str
    assignee_user_id: int | None = None


class TicketUpdate(BaseModel):
    status: str | None = None
    assignee_user_id: int | None = None


class TicketOut(BaseModel):
    id: int
    robot_id: int
    title: str
    description: str
    status: str
    assignee_user_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class TicketLogOut(BaseModel):
    id: int
    ticket_id: int
    action: str
    content: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class TicketAttachmentOut(BaseModel):
    id: int
    ticket_id: int
    file_name: str
    url: str
    created_at: datetime

    class Config:
        from_attributes = True
