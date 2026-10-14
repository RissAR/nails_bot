#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
DB_PATH="${DB_PATH:-./data/nails_salon.db}"
mkdir -p "$BACKUP_DIR"

if [ ! -f "$DB_PATH" ]; then
  if [ -f "./nails_salon.db" ]; then
    DB_PATH="./nails_salon.db"
  else
    echo "Database file not found at $DB_PATH or ./nails_salon.db"
    exit 1
  fi
fi

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/nails_salon_${TIMESTAMP}.db"

sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"
echo "Backup created successfully: $BACKUP_FILE"

# Ротація (видалення бекапів старших за 30 днів)
find "$BACKUP_DIR" -type f -name "nails_salon_*.db" -mtime +30 -delete
echo "Old backups (>30 days) cleaned up."
