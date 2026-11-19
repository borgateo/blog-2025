#!/bin/sh
# Daily: roll up and delete hits older than 13 months.
# Monthly: refresh the DB-IP Lite geo database when it is older than 32 days.
set -eu
cd "$(dirname "$0")"
DATA="${PIXEL_DATA_DIR:?}"
python3 -I pixel.py retention

GEO="$DATA/geo.sqlite3"
if [ -f "$GEO" ] && [ -z "$(find "$GEO" -mtime +32)" ]; then
  exit 0
fi
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# the new month's files appear a few days into the month: fall back to the previous one
for MONTH in "$(date -u +%Y-%m)" "$(date -u -d 'last month' +%Y-%m)"; do
  ok=1
  for kind in country asn; do
    curl -fsS --max-time 300 -o "$TMP/$kind.csv.gz" "https://download.db-ip.com/free/dbip-$kind-lite-$MONTH.csv.gz" || ok=0
  done
  [ "$ok" = 1 ] && break
done
[ "$ok" = 1 ] || { echo "DB-IP download failed" >&2; exit 1; }
python3 -I pixel.py build-geo "$TMP/country.csv.gz" "$TMP/asn.csv.gz"
