#!/usr/bin/env bash

# Render.com Start Script for CoreSync Django App
# Optimized for 29.09.2025

set -o errexit  # exit on error

echo "🚀 Starting CoreSync Django server..."

# Navigate to Django project directory
cd coresync_backend

# Start Gunicorn server optimized for Render
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
