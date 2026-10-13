import json
from urllib.parse import parse_qs, unquote
from fastapi import APIRouter, Header, Query
from pydantic import BaseModel
from sqlalchemy import select

from src.config import settings
from src.database.models import User
from src.database.session import async_session_maker

router = APIRouter(prefix="/auth", tags=["Auth"])


class UserAuthResponse(BaseModel):
    telegram_id: int | None
    role: str
    first_name: str | None
    username: str | None
    discount_percent: int = 0


@router.get("/me", response_model=UserAuthResponse)
async def get_current_user(
    tg_id: int | None = Query(None, description="Telegram ID in dev mode"),
    init_data: str | None = Query(None, description="Telegram WebApp initData query string"),
    x_telegram_init_data: str | None = Header(None, alias="X-Telegram-Init-Data"),
    discount_override: int | None = None,
) -> UserAuthResponse:
    """Validate user from initData or dev tg_id and return role and loyalty discount."""
    resolved_tg_id: int | None = tg_id
    first_name: str | None = None
    username: str | None = None

    raw_init_data = init_data or x_telegram_init_data
    if raw_init_data:
        try:
            parsed = parse_qs(raw_init_data)
            if "user" in parsed:
                user_json = unquote(parsed["user"][0])
                user_obj = json.loads(user_json)
                resolved_tg_id = user_obj.get("id")
                first_name = user_obj.get("first_name")
                username = user_obj.get("username")
        except Exception:
            pass

    if resolved_tg_id is None:
        return UserAuthResponse(
            telegram_id=None,
            role="client",
            first_name="Гість",
            username=None,
            discount_percent=0,
        )

    # Check if admin
    is_admin = resolved_tg_id in settings.ADMIN_IDS

    discount_percent = 0
    # Check in DB
    async with async_session_maker() as session:
        u_stmt = select(User).where(User.telegram_id == resolved_tg_id)
        u_res = await session.execute(u_stmt)
        user = u_res.scalar_one_or_none()

        role = "admin" if is_admin else (user.role if user else "client")
        if user and not first_name:
            first_name = user.full_name
        if user and not username:
            username = user.username
        if user:
            _, discount_percent = user.loyalty_info

    return UserAuthResponse(
        telegram_id=resolved_tg_id,
        role=role,
        first_name=first_name or ("Адміністратор" if role == "admin" else "Клієнт"),
        username=username,
        discount_percent=discount_percent,
    )
