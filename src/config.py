import json
from typing import Any, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str = "YOUR_BOT_TOKEN_HERE"
    ADMIN_IDS: list[int] = [8607080614]
    DATABASE_URL: str = "sqlite+aiosqlite:///./nails_salon.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: Any) -> list[int]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [int(x) for x in parsed]
                except Exception:
                    v = v[1:-1]
            return [int(item.strip()) for item in v.split(",") if item.strip()]
        if isinstance(v, int):
            return [v]
        if isinstance(v, list):
            return [int(x) for x in v]
        return list(v)


settings = Settings()
