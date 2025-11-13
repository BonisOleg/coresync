#!/usr/bin/env bash

# Render.com Start Script for CoreSync Django App
# Runs migrations before starting the server

set -o errexit  # exit on error

echo "🚀 Starting CoreSync service..."
cd coresync_backend

# Wait for database to be ready
echo "⏳ Waiting for database..."
python << END
import time
import sys
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.db import connection
from django.db.utils import OperationalError

max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        connection.ensure_connection()
        print("✅ Database is ready!")
        break
    except OperationalError as e:
        retry_count += 1
        print(f"⏳ Database not ready yet ({retry_count}/{max_retries}): {e}")
        if retry_count >= max_retries:
            print("❌ Database connection timeout!")
            sys.exit(1)
        time.sleep(2)
END

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

# Start gunicorn
echo "🌐 Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class gthread \
    --threads 4 \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -
