from typing import Any, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.interfaces import BaseRepository
from src.core.db.models.invitations import Invitations


class InvitationsRepo(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self._session: AsyncSession = session

    async def get_by_id(self, invitation_id: UUID) -> Invitations | None:
        invitation = await self._session.get(Invitations, invitation_id)
        return cast(Invitations | None, invitation)

    async def get_all(self) -> list[Invitations]:
        result = await self._session.execute(select(Invitations))
        invitations = result.scalars().all()
        return cast(list[Invitations], invitations)

    async def create(self, data: dict[str, Any]) -> Invitations:
        invitation = Invitations(**data)
        self._session.add(invitation)
        await self._session.flush()
        await self._session.refresh(invitation)
        return invitation

    async def update(self, invitation_id: UUID, data: dict[str, Any]) -> Invitations | None:
        invitation = await self.get_by_id(invitation_id)
        if invitation is None:
            return None

        for field, value in data.items():
            setattr(invitation, field, value)

        await self._session.flush()
        await self._session.refresh(invitation)
        return invitation

    async def delete(self, invitation_id: UUID) -> bool:
        invitation = await self.get_by_id(invitation_id)
        if invitation is None:
            return False

        await self._session.delete(invitation)
        await self._session.flush()
        return True
