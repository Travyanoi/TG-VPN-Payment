from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any

T = TypeVar("T")


class BaseRepository(Generic[T], ABC):
    @abstractmethod
    def create(self, **kwargs: Any) -> T:
        ...

    @abstractmethod
    def save(self, instance: T) -> T:
        ...

    @abstractmethod
    def delete(self, instance: T) -> None:
        ...
