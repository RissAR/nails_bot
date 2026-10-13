from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database.models import Category, Service
from src.database.session import async_session_maker

router = APIRouter(prefix="/services", tags=["Services"])


class ServiceItem(BaseModel):
    id: int
    category_id: int
    category_name: str
    name: str
    description: str | None
    duration_minutes: int
    price: float
    is_active: bool
    master_ids: list[int]


class CategoryItem(BaseModel):
    id: int
    name: str
    slug: str


@router.get("", response_model=list[ServiceItem])
async def get_services() -> list[ServiceItem]:
    """Return all active services with their category and masters."""
    async with async_session_maker() as session:
        stmt = (
            select(Service)
            .options(selectinload(Service.category), selectinload(Service.masters))
            .where(Service.is_active == True)  # noqa: E712
            .order_by(Service.category_id, Service.price)
        )
        result = await session.execute(stmt)
        services = result.scalars().all()

        return [
            ServiceItem(
                id=s.id,
                category_id=s.category_id,
                category_name=s.category.name if s.category else "",
                name=s.name,
                description=s.description,
                duration_minutes=s.duration_minutes,
                price=s.price,
                is_active=s.is_active,
                master_ids=[m.id for m in s.masters],
            )
            for s in services
        ]


@router.get("/categories", response_model=list[CategoryItem])
async def get_categories() -> list[CategoryItem]:
    """Return all categories."""
    async with async_session_maker() as session:
        stmt = select(Category).order_by(Category.id)
        result = await session.execute(stmt)
        categories = result.scalars().all()
        return [CategoryItem(id=c.id, name=c.name, slug=c.slug) for c in categories]
