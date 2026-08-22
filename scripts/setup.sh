#!/usr/bin/env bash
# Set up the Python environment and generate/load data against
# whichever local MySQL .env currently points at.
#
# Prerequisite: the sql_gym database and gym_user account must already
# exist -- run scripts/bootstrap_local_mysql.sh first if you haven't,
# and the schema files in database/ must already be applied.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example -- edit it before continuing."
  exit 1
fi

echo "Setting up Python environment for data generation..."
cd data_generation
PYTHON_BIN=$(command -v python3 || command -v python)
if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv
fi
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
pip install -q -r requirements.txt

echo "Generating and loading data..."
python generate_data.py
cd ..

source .env
echo "Setup complete. Connect with:"
echo "  mysql -h ${MYSQL_HOST:-127.0.0.1} -P ${MYSQL_PORT:-3306} -u ${MYSQL_USER:-gym_user} -p ${MYSQL_DATABASE:-sql_gym}"
