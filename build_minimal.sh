#!/usr/bin/env bash
# ULTRA MINIMAL BUILD - Last Resort

set -e

echo "🚀 MINIMAL Django build..."

# Only essential packages
pip install Django==5.1.1 gunicorn==22.0.0 whitenoise==6.7.0 psycopg[binary]==3.2.3 python-decouple==3.8 djangorestframework==3.15.2

# Go to Django project
cd coresync_backend

# Essential Django setup
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "✅ Minimal build complete!"
