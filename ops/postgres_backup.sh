#!/usr/bin/env sh
set -eu

DESTINATION="${HELIOS_BACKUP_DESTINATION:-/backups}"
INTERVAL="${HELIOS_BACKUP_INTERVAL_SECONDS:-86400}"
KEEP="${HELIOS_BACKUP_KEEP:-7}"

mkdir -p "$DESTINATION"

while true; do
  TIMESTAMP="$(date +%s)"
  TARGET="$DESTINATION/helios-postgres-$TIMESTAMP.sql.gz"
  pg_dump "$HELIOS_DATABASE_URL" | gzip > "$TARGET"
  find "$DESTINATION" -name 'helios-postgres-*.sql.gz' -type f -print0 \
    | xargs -0 ls -1t \
    | tail -n "+$((KEEP + 1))" \
    | xargs -r rm -f
  printf 'Created HELIOS PostgreSQL backup: %s\n' "$TARGET"
  sleep "$INTERVAL"
done
