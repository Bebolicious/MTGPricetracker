#!/bin/bash
# Build script for MTG Price Tracker

echo "Building MTG Price Tracker..."

# Install PyInstaller if not already installed
pip install pyinstaller

# Clean previous builds
rm -rf build dist

# Build the executable
pyinstaller mtgpricer.spec

# Check if build was successful
if [ -f "dist/mtgpricer" ]; then
    echo "Build successful! Executable created at: dist/mtgpricer"
    echo "You can run it with: ./dist/mtgpricer"
else
    echo "Build failed!"
    exit 1
fi

