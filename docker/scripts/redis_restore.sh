#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <dump.rdb>"
  exit 1
fi

BACKUP_FILE="$1"
if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/docker/docker-compose.prod.yml}"

docker compose -f "$COMPOSE_FILE" cp "$BACKUP_FILE" redis:/data/dump.rdb
docker compose -f "$COMPOSE_FILE" restart redis

echo "Redis restore completed from: $BACKUP_FILE"
