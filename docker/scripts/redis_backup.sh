#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/docker/docker-compose.prod.yml}"
OUTPUT_DIR="${1:-$ROOT_DIR/backups/redis}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT_FILE="$OUTPUT_DIR/redis_${TIMESTAMP}.rdb"

mkdir -p "$OUTPUT_DIR"

BEFORE_LASTSAVE="$(docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli LASTSAVE | tr -d '\r')"
docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli BGSAVE > /dev/null

for _ in {1..30}; do
  AFTER_LASTSAVE="$(docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli LASTSAVE | tr -d '\r')"
  if [[ "$AFTER_LASTSAVE" -gt "$BEFORE_LASTSAVE" ]]; then
    break
  fi
  sleep 1
done

docker compose -f "$COMPOSE_FILE" cp redis:/data/dump.rdb "$OUTPUT_FILE"

echo "Redis backup saved to: $OUTPUT_FILE"
