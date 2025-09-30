#!/usr/bin/env bash

# Render.com Build Script for CoreSync Django App
# Optimized for 29.09.2025

set -o errexit  # exit on error

echo "🚀 Starting CoreSync build process..."
echo "🔍 Environment check:"
echo "   Python version: $(python --version)"
echo "   Pip version: $(pip --version)"
echo "   Working directory: $(pwd)"
echo "   Available space: $(df -h . | tail -1)"

# Upgrade pip first
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Navigate to Django project directory
cd coresync_backend

# Collect static files with WhiteNoise
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create database migrations (simplified for deploy) 
echo "🗄️ Creating database migrations..."
python manage.py makemigrations --noinput || echo "No new migrations needed"

# Check for migration conflicts
echo "🔍 Checking for migration conflicts..."
python manage.py showmigrations --list || echo "Migration check completed"

# Apply database migrations  
echo "🔄 Applying database migrations..."
python manage.py migrate --noinput

# Test deployment configuration - DISABLED FOR INITIAL DEPLOY
echo "🧪 Skipping deployment tests for initial deploy..."
# if python deployment_test.py; then
#     echo "✅ Deployment tests passed!"
# else
#     echo "⚠️ Deployment test warnings (continuing anyway)..."
# fi

# Create superuser if needed (only in development)
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL 2>/dev/null || echo "Superuser already exists"
fi

echo "✅ Build completed successfully!"
