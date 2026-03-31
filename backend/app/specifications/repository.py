from typing import TypeVar

from sqlalchemy.orm import Query
from sqlalchemy.sql import Select

from app.specifications.base import Specification

T = TypeVar("T")


class SpecificationRepository:
    @staticmethod
    def apply_specification(query: Select, spec: Specification[T]) -> Select:
        return spec.apply_to_query(query)

    @staticmethod
    def apply_specifications(query: Select, specs: list[Specification[T]]) -> Select:
        result = query
        for spec in specs:
            result = spec.apply_to_query(result)
        return result
