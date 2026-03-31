from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.repositories.base import BaseRepository
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[ModelType, RepositoryType]):
    def __init__(self, repository: RepositoryType):
        self.repository = repository

    def get(self, id: int) -> ModelType:
        obj = self.repository.get(id)
        if not obj:
            raise NotFoundException(self._get_resource_name(), id)
        return obj

    def get_or_none(self, id: int) -> ModelType | None:
        return self.repository.get(id)

    def list(self, limit: int = 100, offset: int = 0) -> list[ModelType]:
        return self.repository.list(limit, offset)

    def create(self, obj_in: dict) -> ModelType:
        obj = self.repository.create(obj_in)
        self.repository.commit()
        return self.repository.refresh(obj)

    def update(self, id: int, obj_in: dict) -> ModelType:
        obj = self.get(id)
        self.repository.update(obj, obj_in)
        self.repository.commit()
        return self.repository.refresh(obj)

    def delete(self, id: int) -> None:
        obj = self.get(id)
        self.repository.delete(obj)
        self.repository.commit()

    def _get_resource_name(self) -> str:
        return "资源"
