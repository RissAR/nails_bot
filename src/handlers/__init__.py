from src.handlers.admin import admin_router
from src.handlers.client import client_router
from src.handlers.common import common_router

__all__ = [
    "admin_router",
    "client_router",
    "common_router",
]
