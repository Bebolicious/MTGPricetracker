@echo off
REM Build script for MTG Price Tracker (Windows)

echo Building MTG Price Tracker...

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
pyinstaller mtgpricer.spec

REM Check if build was successful
if exist "dist\mtgpricer.exe" (
    echo Build successful! Executable created at: dist\mtgpricer.exe
    echo You can run it by double-clicking or from cmd: dist\mtgpricer.exe
) else (
    echo Build failed!
    exit /b 1
)

