from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def get(self, id: int) -> ModelType | None:
        return self.db.get(self.model, id)

    def get_by_field(self, field: str, value: Any) -> ModelType | None:
        return self.db.query(self.model).filter(getattr(self.model, field) == value).first()

    def list(self, limit: int = 100, offset: int = 0) -> list[ModelType]:
        return self.db.query(self.model).offset(offset).limit(limit).all()

    def create(self, obj_in: dict) -> ModelType:
        obj = self.model(**obj_in)
        self.db.add(obj)
        self.db.flush()
        return obj

    def update(self, obj: ModelType, obj_in: dict) -> ModelType:
        for key, value in obj_in.items():
            if value is not None:
                setattr(obj, key, value)
        self.db.flush()
        return obj

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, obj: ModelType) -> ModelType:
        self.db.refresh(obj)
        return obj
