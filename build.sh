#!/usr/bin/env bash

# Render.com Build Script for CoreSync Django App
# Optimized for 29.09.2025

set -o errexit  # exit on error

echo "🚀 Starting CoreSync build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Navigate to Django project directory
cd coresync_backend

# Collect static files with WhiteNoise
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create database migrations
echo "🗄️ Creating database migrations..."
python manage.py makemigrations --noinput || echo "No new migrations needed"

# Apply database migrations  
echo "🔄 Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if needed (only in development)
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL 2>/dev/null || echo "Superuser already exists"
fi

echo "✅ Build completed successfully!"
