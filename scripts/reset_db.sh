#!/usr/bin/env bash
# Drop and recreate the schema against whichever MySQL .env currently
# points at, then regenerate all data from scratch.
#
# Uses gym_user (from .env) for the schema reload, since DDL here
# (DROP/CREATE TABLE) only requires privileges on the sql_gym database
# itself, which bootstrap_local_mysql.sh already granted it.
set -euo pipefail
cd "$(dirname "$0")/.."

source .env
MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_USER="${MYSQL_USER:-gym_user}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-gym_pw}"
MYSQL_DATABASE="${MYSQL_DATABASE:-sql_gym}"

MYSQL_BIN=$(command -v mysql || echo "/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe")

echo "Reapplying schema..."
for f in database/01_create_database.sql database/02_schema.sql database/03_indexes.sql database/04_views.sql; do
  echo "  applying $f"
  "$MYSQL_BIN" -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" < "$f"
done

echo "Regenerating data..."
cd data_generation
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
python generate_data.py
cd ..

echo "Running validation checks..."
"$MYSQL_BIN" -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" < database/05_validation.sql

echo "Reset complete."
