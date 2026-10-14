import hashlib
import hmac
import json
import logging
import time
import urllib.parse
from fastapi import Depends, Header, HTTPException, Query, Request, status

from src.config import settings

logger = logging.getLogger(__name__)


def validate_telegram_init_data(init_data_raw: str, bot_token: str) -> dict | None:
    """
    Validate Telegram WebApp initData string using HMAC-SHA256 signature verification.
    Ensures data integrity and prevents replay attacks (>24h).
    """
    if not init_data_raw or not bot_token:
        return None

    try:
        parsed_items = urllib.parse.parse_qsl(init_data_raw, keep_blank_values=True)
        items = dict(parsed_items)

        received_hash = items.pop("hash", None)
        if not received_hash:
            logger.warning("Telegram initData missing 'hash' parameter")
            return None

        # Data check string is alphabetically sorted key=value pairs joined with \n
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(items.items()))

        # Secret key: HMAC-SHA256 of bot_token using "WebAppData" as key
        secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()

        # Calculated hash: HMAC-SHA256 of data_check_string using secret_key
        calculated_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(calculated_hash, received_hash):
            logger.warning("Telegram initData HMAC hash mismatch")
            return None

        # Replay attack protection (auth_date must not be older than 24 hours / 86400s)
        auth_date_str = items.get("auth_date")
        if not auth_date_str:
            logger.warning("Telegram initData missing 'auth_date'")
            return None

        auth_date = int(auth_date_str)
        if abs(time.time() - auth_date) > 86400:
            logger.warning("Telegram initData expired (auth_date: %d)", auth_date)
            return None

        user_data = {}
        user_str = items.get("user")
        if user_str:
            try:
                user_data = json.loads(user_str)
            except Exception as e:
                logger.warning("Failed to decode user json in initData: %s", e)

        telegram_id = user_data.get("id")
        return {
            "telegram_id": int(telegram_id) if telegram_id else None,
            "first_name": user_data.get("first_name"),
            "username": user_data.get("username"),
            "auth_date": auth_date,
            "user": user_data,
            "raw_data": items,
        }
    except Exception as e:
        logger.error("Error validating telegram initData: %s", e)
        return None


async def get_current_telegram_user(
    request: Request,
    x_telegram_init_data: str | None = Header(None, alias="X-Telegram-Init-Data"),
    init_data: str | None = Query(None),
    tg_id: int | None = Query(None),
) -> dict:
    """
    FastAPI dependency resolving current user from Telegram initData (Header or Query)
    or local dev query tg_id.
    """
    init_data_raw = x_telegram_init_data or init_data

    if init_data_raw:
        validated = validate_telegram_init_data(init_data_raw, settings.BOT_TOKEN)
        if validated and validated.get("telegram_id"):
            tg_user_id = validated["telegram_id"]
            role = "admin" if tg_user_id in settings.ADMIN_IDS else "client"
            validated["role"] = role
            validated["is_authenticated"] = True
            return validated
        else:
            logger.warning("Provided initData failed cryptographic validation")

    # Local development / fallback mode when tg_id is supplied without valid initData
    if tg_id is not None:
        if not settings.BOT_TOKEN or tg_id in settings.ADMIN_IDS:
            role = "admin" if tg_id in settings.ADMIN_IDS else "client"
            return {
                "telegram_id": tg_id,
                "role": role,
                "first_name": "Адміністратор" if role == "admin" else "Клієнт",
                "username": None,
                "is_authenticated": True,
                "dev_mode": True,
            }

    # Guest context
    return {
        "telegram_id": None,
        "role": "guest",
        "first_name": "Гість",
        "username": None,
        "is_authenticated": False,
    }


async def verify_admin_access(
    user: dict = Depends(get_current_telegram_user),
) -> dict:
    """
    FastAPI dependency ensuring the requesting user has verified admin rights.
    Blocks unauthorized requests with HTTP 403 Forbidden.
    """
    tg_id = user.get("telegram_id")
    if not tg_id or tg_id not in settings.ADMIN_IDS or not user.get("is_authenticated"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ заборонено: потрібні права адміністратора.",
        )
    return user
