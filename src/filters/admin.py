from typing import Optional
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, User as TgUser

from src.config import settings
from src.database.models.user import User as DbUser


class IsAdminFilter(BaseFilter):
    """Filter that checks if a user is an administrator."""

    async def __call__(
        self,
        event: TelegramObject,
        event_from_user: Optional[TgUser] = None,
        db_user: Optional[DbUser] = None,
    ) -> bool:
        user = event_from_user or getattr(event, "from_user", None)
        if user and user.id in settings.ADMIN_IDS:
            return True

        if db_user and db_user.role == "admin":
            return True

        return False
