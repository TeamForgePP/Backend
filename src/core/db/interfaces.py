from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def get_by_id(self, id_: UUID) -> Any | None:
        """Получить объект по id или вернуть None."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Any]:
        """Получить все объекты."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: dict[str, Any]) -> Any:
        """Создать объект из словаря полей и вернуть его."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, id_: UUID, data: dict[str, Any]) -> Any | None:
        """Обновить объект по id, вернуть обновлённый объект или None."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id_: UUID) -> bool:
        """Удалить объект по id. Вернуть True, если удалён, иначе False."""
        raise NotImplementedError
