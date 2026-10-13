from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TgUser
from sqlalchemy import select

from src.config import settings
from src.database.models.user import User
from src.database.session import async_session_maker


class AuthMiddleware(BaseMiddleware):
    """Middleware for automatic user registration and role management."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        event_from_user: TgUser | None = data.get("event_from_user")
        if not event_from_user:
            return await handler(event, data)

        async with async_session_maker() as session:
            stmt = select(User).where(User.telegram_id == event_from_user.id)
            result = await session.execute(stmt)
            db_user = result.scalar_one_or_none()

            is_admin = event_from_user.id in settings.ADMIN_IDS

            if db_user is None:
                db_user = User(
                    telegram_id=event_from_user.id,
                    username=event_from_user.username,
                    full_name=event_from_user.full_name or "Unknown",
                    role="admin" if is_admin else "client",
                )
                session.add(db_user)
                await session.commit()
                await session.refresh(db_user)
            else:
                updated = False
                if is_admin and db_user.role != "admin":
                    db_user.role = "admin"
                    updated = True
                if event_from_user.username != db_user.username:
                    db_user.username = event_from_user.username
                    updated = True
                if (
                    event_from_user.full_name
                    and event_from_user.full_name != db_user.full_name
                ):
                    db_user.full_name = event_from_user.full_name
                    updated = True

                if updated:
                    await session.commit()
                    await session.refresh(db_user)

            data["db_user"] = db_user
            data["session"] = session

            return await handler(event, data)
