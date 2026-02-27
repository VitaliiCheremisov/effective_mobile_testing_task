#!/bin/sh
set -e
cd /app

# Wait for PostgreSQL to accept connections
i=0
while [ $i -lt 30 ]; do
  if python -c "
import os, sys
url = os.environ.get('DATABASE_URL', '')
if not url:
    sys.exit(1)
import psycopg
conn = psycopg.connect(url)
conn.close()
" 2>/dev/null; then
    break
  fi
  i=$((i + 1))
  [ $i -eq 30 ] && echo "Database not ready." && exit 1
  sleep 1
done

python manage.py migrate --noinput
exec "$@"
