#!/usr/bin/env bash

# Render.com Build Script for CoreSync Django App
# Fixed: Database operations moved to start command

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

# Collect static files with WhiteNoise (no DB required)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Build completed successfully!"
echo "ℹ️  Database migrations will run on service start"
