#!/bin/bash
# iOS build script for CoreSync

set -e  # Exit on error

echo "🍎 Building CoreSync iOS app..."

# Clean
echo "Cleaning previous builds..."
flutter clean

# Get dependencies
echo "Getting dependencies..."
flutter pub get

# Build
echo "Building iOS release..."
flutter build ios --release --no-codesign

echo "✅ iOS build complete!"
echo "📦 Open Xcode to sign and upload:"
echo "   open ios/Runner.xcworkspace"
echo ""
echo "Next steps:"
echo "  1. Open Xcode workspace"
echo "  2. Select Runner → Signing & Capabilities"
echo "  3. Select your Team"
echo "  4. Product → Archive"
echo "  5. Distribute App → App Store Connect"

