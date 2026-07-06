#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/docker/docker-compose.prod.yml}"
OUTPUT_DIR="${1:-$ROOT_DIR/backups/postgres}"
POSTGRES_USER="${POSTGRES_USER:-peskovp}"
POSTGRES_DB="${POSTGRES_DB:-peskovp}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT_FILE="$OUTPUT_DIR/${POSTGRES_DB}_${TIMESTAMP}.sql.gz"

mkdir -p "$OUTPUT_DIR"

docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip -c > "$OUTPUT_FILE"

echo "PostgreSQL backup saved to: $OUTPUT_FILE"
