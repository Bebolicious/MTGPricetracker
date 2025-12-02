@echo off
REM Build script for MTG Price Tracker (Windows)

echo Building MTG Price Tracker...

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
pyinstaller mtg_price_tracker.spec

REM Check if build was successful
if exist "dist\mtg_price_tracker.exe" (
    echo Build successful! Executable created at: dist\mtg_price_tracker.exe
    echo You can run it by double-clicking or from cmd: dist\mtg_price_tracker.exe
) else (
    echo Build failed!
    exit /b 1
)

