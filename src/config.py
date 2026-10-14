import json
from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str = ""
    ADMIN_IDS: list[int] = []
    ADMIN_USERNAME: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/nails_salon.db"
    SALON_NAME: str = "Sense Nail Studio"
    WEBAPP_URL: str = "http://localhost:8000/app"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    APP_VERSION: str = "1.0.1"

    def get_webapp_url(self, extra_params: dict[str, str] | None = None) -> str:
        """Generate WebApp URL with cache-busting version parameter."""
        params = {"v": self.APP_VERSION}
        if extra_params:
            params.update(extra_params)
        query = "&".join(f"{k}={v}" for k, v in params.items())
        base = self.WEBAPP_URL.rstrip("/")
        sep = "&" if "?" in base else "?"
        return f"{base}{sep}{query}"

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
