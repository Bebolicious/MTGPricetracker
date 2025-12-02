#!/bin/bash
# Build script for MTG Price Tracker

echo "Building MTG Price Tracker..."

# Install PyInstaller if not already installed
pip install pyinstaller

# Clean previous builds
rm -rf build dist

# Build the executable
pyinstaller mtg_price_tracker.spec

# Check if build was successful
if [ -f "dist/mtg_price_tracker" ]; then
    echo "Build successful! Executable created at: dist/mtg_price_tracker"
    echo "You can run it with: ./dist/mtg_price_tracker"
else
    echo "Build failed!"
    exit 1
fi

