from datetime import datetime

from pydantic import BaseModel


class ConfigUpsert(BaseModel):
    key: str
    value: str


class ConfigOut(BaseModel):
    id: int
    key: str
    value: str
    updated_at: datetime

    class Config:
        from_attributes = True
