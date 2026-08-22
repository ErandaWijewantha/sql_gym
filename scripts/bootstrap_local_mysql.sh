#!/usr/bin/env bash
# One-time bootstrap against a LOCAL MySQL install (not Docker):
# creates the sql_gym database and a low-privilege gym_user account
# scoped to it, using root only for this one setup step.
#
# Requires MYSQL_ROOT_PASSWORD to be set in .env beforehand.
set -euo pipefail
cd "$(dirname "$0")/.."

source .env

if [ -z "${MYSQL_ROOT_PASSWORD:-}" ]; then
  echo "Set MYSQL_ROOT_PASSWORD in .env first, then re-run this script." >&2
  exit 1
fi

MYSQL_BIN="/c/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe"

"$MYSQL_BIN" -h 127.0.0.1 -P "${MYSQL_PORT:-3306}" -u root -p"$MYSQL_ROOT_PASSWORD" <<SQL
CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE}
    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'localhost' IDENTIFIED BY '${MYSQL_PASSWORD}';
GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO '${MYSQL_USER}'@'%';
GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO '${MYSQL_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "Bootstrap complete: database '${MYSQL_DATABASE}' and user '${MYSQL_USER}' are ready."
echo "You can now blank out MYSQL_ROOT_PASSWORD in .env -- it is not needed again."
