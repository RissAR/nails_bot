from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database.models import Master
from src.database.session import async_session_maker

router = APIRouter(prefix="/masters", tags=["Masters"])


class MasterItem(BaseModel):
    id: int
    name: str
    title: str
    bio: str | None
    is_active: bool
    service_ids: list[int]


@router.get("", response_model=list[MasterItem])
async def get_masters() -> list[MasterItem]:
    """Return all active masters with their services."""
    async with async_session_maker() as session:
        stmt = (
            select(Master)
            .options(selectinload(Master.services))
            .where(Master.is_active == True)  # noqa: E712
            .order_by(Master.id)
        )
        result = await session.execute(stmt)
        masters = result.scalars().all()

        return [
            MasterItem(
                id=m.id,
                name=m.name,
                title=m.title,
                bio=m.bio,
                is_active=m.is_active,
                service_ids=[s.id for s in m.services],
            )
            for m in masters
        ]
