from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy import and_, or_, not_
from sqlalchemy.sql import Select

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        pass

    @abstractmethod
    def apply_to_query(self, query: Select) -> Select:
        pass

    def and_(self, other: "Specification[T]") -> "AndSpecification[T]":
        return AndSpecification(self, other)

    def or_(self, other: "Specification[T]") -> "OrSpecification[T]":
        return OrSpecification(self, other)

    def not_(self) -> "NotSpecification[T]":
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)

    def apply_to_query(self, query: Select) -> Select:
        return query.where(and_(self.left.apply_to_query(query).whereclause, self.right.apply_to_query(query).whereclause))


class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)

    def apply_to_query(self, query: Select) -> Select:
        return query.where(or_(self.left.apply_to_query(query).whereclause, self.right.apply_to_query(query).whereclause))


class NotSpecification(Specification[T]):
    def __init__(self, spec: Specification[T]):
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)

    def apply_to_query(self, query: Select) -> Select:
        return query.where(not_(self.spec.apply_to_query(query).whereclause))


class FieldSpecification(Specification[T]):
    def __init__(self, field: Any, operator: str, value: Any):
        self.field = field
        self.operator = operator
        self.value = value

    def is_satisfied_by(self, candidate: T) -> bool:
        actual_value = getattr(candidate, self.field.key, None)
        match self.operator:
            case "==":
                return actual_value == self.value
            case "!=":
                return actual_value != self.value
            case ">":
                return actual_value > self.value
            case ">=":
                return actual_value >= self.value
            case "<":
                return actual_value < self.value
            case "<=":
                return actual_value <= self.value
            case "in":
                return actual_value in self.value
            case "like":
                return self.value in str(actual_value)
            case _:
                return False

    def apply_to_query(self, query: Select) -> Select:
        match self.operator:
            case "==":
                return query.where(self.field == self.value)
            case "!=":
                return query.where(self.field != self.value)
            case ">":
                return query.where(self.field > self.value)
            case ">=":
                return query.where(self.field >= self.value)
            case "<":
                return query.where(self.field < self.value)
            case "<=":
                return query.where(self.field <= self.value)
            case "in":
                return query.where(self.field.in_(self.value))
            case "like":
                return query.where(self.field.ilike(f"%{self.value}%"))
            case _:
                return query
