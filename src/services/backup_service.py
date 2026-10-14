import asyncio
from datetime import datetime
import glob
import logging
import os
import sqlite3
import time
from zoneinfo import ZoneInfo

from src.config import settings

logger = logging.getLogger(__name__)

KYIV_TZ = ZoneInfo("Europe/Kyiv")


def get_actual_db_path() -> str:
    """Resolve physical SQLite database file path from settings or fallback."""
    if settings.DATABASE_URL.startswith("sqlite"):
        configured_path = settings.DATABASE_URL.split(":///")[-1]
        if os.path.exists(configured_path):
            return configured_path

    if os.path.exists("./data/nails_salon.db"):
        return "./data/nails_salon.db"
    elif os.path.exists("./nails_salon.db"):
        return "./nails_salon.db"

    return "./data/nails_salon.db"


def cleanup_old_backups(backup_dir: str = "backups", retention_days: int = 30) -> int:
    """Delete backups older than retention_days (default: 30 days)."""
    if not os.path.exists(backup_dir):
        return 0

    deleted_count = 0
    now_ts = time.time()
    cutoff_ts = now_ts - (retention_days * 86400)

    pattern = os.path.join(backup_dir, "nails_salon_*.db")
    for file_path in glob.glob(pattern):
        try:
            mtime = os.path.getmtime(file_path)
            if mtime < cutoff_ts:
                os.remove(file_path)
                deleted_count += 1
                logger.info("Cleaned up old backup: %s (mtime: %s)", file_path, datetime.fromtimestamp(mtime))
        except Exception as e:
            logger.warning("Failed to remove old backup %s: %s", file_path, e)

    if deleted_count > 0:
        logger.info("Total cleaned up old backups: %d", deleted_count)
    return deleted_count


def create_backup(source_db_path: str | None = None, backup_dir: str = "backups") -> str:
    """
    Perform atomic and consistent online SQLite backup using sqlite3.backup().
    Saves snapshot into backup_dir and triggers retention rotation.
    """
    db_file = source_db_path or get_actual_db_path()
    if not os.path.exists(db_file):
        raise FileNotFoundError(f"Database source file not found at '{db_file}'")

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now(KYIV_TZ).strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"nails_salon_{timestamp}.db")

    logger.info("Starting online SQLite backup from %s to %s", db_file, backup_file)
    with sqlite3.connect(db_file) as src_conn:
        with sqlite3.connect(backup_file) as dst_conn:
            src_conn.backup(dst_conn)

    logger.info("Backup created successfully: %s (size: %d bytes)", backup_file, os.path.getsize(backup_file))
    cleanup_old_backups(backup_dir=backup_dir, retention_days=30)
    return backup_file


async def run_backup_worker() -> None:
    """
    Background worker running indefinitely.
    Creates a scheduled backup once per day at 03:00 (Europe/Kyiv time).
    """
    logger.info("Database backup background worker started.")
    last_backup_date = None

    while True:
        try:
            now_kyiv = datetime.now(KYIV_TZ)
            today = now_kyiv.date()

            # Trigger backup at 03:00 Kyiv time
            if now_kyiv.hour == 3 and last_backup_date != today:
                logger.info("Triggering scheduled 03:00 daily backup...")
                create_backup()
                last_backup_date = today

            # Check every 60 seconds
            await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Database backup background worker stopped.")
            break
        except Exception as e:
            logger.error("Error in backup background worker: %s", e, exc_info=True)
            await asyncio.sleep(60)
