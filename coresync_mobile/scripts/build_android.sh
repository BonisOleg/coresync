#!/bin/bash
# Android build script for CoreSync

set -e

echo "🤖 Building CoreSync Android app..."

# Clean
echo "Cleaning previous builds..."
flutter clean

# Get dependencies
echo "Getting dependencies..."
flutter pub get

# Build app bundle
echo "Building Android App Bundle..."
flutter build appbundle --release

echo "✅ Android build complete!"
echo "📦 App bundle location:"
echo "   build/app/outputs/bundle/release/app-release.aab"
echo ""
echo "📦 Upload to Play Console:"
echo "   https://play.google.com/console"
echo ""
echo "Next steps:"
echo "  1. Go to Play Console"
echo "  2. Create new release"
echo "  3. Upload app-release.aab"
echo "  4. Complete store listing"
echo "  5. Submit for review"

