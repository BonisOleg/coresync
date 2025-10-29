#!/bin/bash
# Flutter App Launch Script

echo "🚀 CoreSync Flutter App - Launch Script"
echo "========================================"

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter not found!"
    echo ""
    echo "Flutter is still installing via Homebrew."
    echo "Wait 2-3 more minutes and run this script again."
    echo ""
    echo "Or manually add Flutter to PATH:"
    echo "  export PATH=\"\$PATH:/opt/homebrew/Caskroom/flutter/latest/flutter/bin\""
    exit 1
fi

echo "✅ Flutter found: $(flutter --version | head -n 1)"
echo ""

# Navigate to project
cd /Users/olegbonislavskyi/SPA-AI/coresync_mobile

# Clean previous builds
echo "🧹 Cleaning previous builds..."
flutter clean

# Get dependencies
echo "📦 Installing dependencies (40+ packages, will take 2-3 min)..."
flutter pub get

# Check for devices
echo ""
echo "📱 Available devices:"
flutter devices

echo ""
echo "Choose how to run:"
echo "  1. Chrome (recommended for quick UI test)"
echo "  2. iOS Simulator (if available)"
echo "  3. Android Emulator (if available)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "🌐 Launching in Chrome..."
        flutter run -d chrome
        ;;
    2)
        echo "🍎 Opening iOS Simulator..."
        open -a Simulator
        echo "⏳ Waiting 30 seconds for Simulator to start..."
        sleep 30
        echo "🚀 Launching app..."
        flutter run
        ;;
    3)
        echo "🤖 Launching in Android Emulator..."
        flutter run -d android
        ;;
    *)
        echo "❌ Invalid choice. Run script again."
        exit 1
        ;;
esac

