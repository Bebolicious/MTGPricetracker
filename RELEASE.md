# Release Guide

This guide explains how to create downloadable installers for Windows and Linux.

## Automated Builds (Recommended)

The project uses GitHub Actions to automatically build releases for both platforms.

### Creating a Release

1. **Update version** in your code (if you have a version file)

2. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Prepare release v1.0.0"
   ```

3. **Create and push a tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **GitHub Actions will automatically**:
   - Build for Linux
   - Build for Windows
   - Create a GitHub Release
   - Attach both executables to the release

5. **View your release** at: `https://github.com/yourusername/MTGPricetracker/releases`

### Manual Release (if needed)

If you want to manually create a release on GitHub:

1. Push your tag as shown above
2. Go to your repository on GitHub
3. Click "Releases" → "Create a new release"
4. Select your tag (e.g., v1.0.0)
5. Add release notes
6. The executables will be automatically attached by GitHub Actions

## Local Builds

### Linux

```bash
# Install dependencies
pip install pyinstaller

# Run build script
./build.sh

# Or manually:
pyinstaller mtg_price_tracker.spec

# Executable will be in: dist/mtg_price_tracker
```

### Windows

```bash
# Install dependencies
pip install pyinstaller

# Run build script
build.bat

# Or manually:
pyinstaller mtg_price_tracker.spec

# Executable will be in: dist\mtg_price_tracker.exe
```

## Testing the Executable

### Linux
```bash
./dist/mtg_price_tracker
```

### Windows
Double-click `dist\mtg_price_tracker.exe` or run from cmd:
```cmd
dist\mtg_price_tracker.exe
```

## Distribution

Users can download the executable for their platform from your GitHub Releases page:
- **Linux users**: Download `mtg_price_tracker-linux`, make it executable (`chmod +x`), and run it
- **Windows users**: Download `mtg_price_tracker-windows.exe` and double-click to run

No Python installation required! The executables are standalone and include all dependencies.

## Version Numbering

Follow semantic versioning:
- `v1.0.0` - Major release
- `v1.1.0` - Minor update (new features)
- `v1.0.1` - Patch (bug fixes)

## Troubleshooting

### Build fails on Linux
- Make sure you have Python 3.8+ installed
- Install system dependencies if needed: `sudo apt-get install python3-dev`

### Build fails on Windows
- Make sure Python is in your PATH
- Run build.bat from Command Prompt (not PowerShell)

### Executable doesn't run
- Check that the user has execution permissions (Linux)
- Check antivirus hasn't blocked it (Windows)
- Make sure the data/ folder can be created in the same directory

## File Size

The executables will be larger (~50-100MB) because they bundle:
- Python interpreter
- All dependencies (textual, httpx, etc.)
- SQLite database engine

This is normal for PyInstaller builds!

