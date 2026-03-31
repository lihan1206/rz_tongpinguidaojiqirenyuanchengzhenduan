from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Repository基类，提供基本的CRUD操作"""

    def __init__(self, model: Type[ModelType]):
        """
        初始化Repository

        :param model: SQLAlchemy模型类
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """根据ID获取单个实体"""
        return db.get(self.model, id)

    def get_by(self, db: Session, **kwargs) -> Optional[ModelType]:
        """根据条件获取单个实体"""
        return db.execute(select(self.model).filter_by(**kwargs)).scalar_one_or_none()

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[Any] = None,
        **kwargs,
    ) -> List[ModelType]:
        """获取实体列表，支持分页和条件过滤"""
        query = select(self.model)

        if kwargs:
            query = query.filter_by(**kwargs)

        if order_by is not None:
            query = query.order_by(order_by)
        else:
            # 默认按id降序
            if hasattr(self.model, "id"):
                query = query.order_by(self.model.id.desc())

        query = query.offset(skip).limit(limit)
        return db.execute(query).scalars().all()

    def count(self, db: Session, **kwargs) -> int:
        """统计实体数量"""
        query = select(self.model)
        if kwargs:
            query = query.filter_by(**kwargs)
        return db.execute(query).scalar_one_or_none() or 0

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """创建新实体"""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """更新实体"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: Any) -> Optional[ModelType]:
        """删除实体"""
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def exists(self, db: Session, **kwargs) -> bool:
        """检查是否存在符合条件的实体"""
        query = select(self.model).filter_by(**kwargs).exists()
        return db.execute(select(query)).scalar()