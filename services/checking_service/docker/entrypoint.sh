#!/bin/sh
set -e

for i in $(seq 1 30)
do
  if pg_isready \
      -h "$DB_HOST" \
      -p "$DB_PORT" \
      -U "$DB_USER"
  then
      exec "$@"
  fi

  sleep 2
done

echo "Database unavailable"
exit 1