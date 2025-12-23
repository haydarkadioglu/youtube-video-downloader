# Build Instructions

## Building Windows Executable

### Quick Build
```bash
python build.py
```

This will:
1. Install PyInstaller if needed
2. Build the executable using the spec file
3. Output to `dist/YouTube-Downloader.exe`

### Manual Build
```bash
# Install PyInstaller
pip install pyinstaller

# Build with spec file
pyinstaller youtube-downloader.spec --clean

# Or build with command line options
pyinstaller --name="YouTube-Downloader" ^
            --noconsole ^
            --onefile ^
            --add-data="resources/styles.qss;resources" ^
            main.py
```

### Create Release Package
```bash
# Build first
python build.py

# Then create release ZIP
python create_release.py
```

This creates `release/yt-video-downloader-v1.0.0-windows.zip` ready for GitHub Releases.

## Build Options

### Console vs No Console
- `--noconsole` or `--windowed` - No console window (GUI only)
- `--console` - Show console for debugging

### Single File vs Directory
- `--onefile` - Single .exe file (slower start)
- Default - Directory with dependencies (faster start)

### Icon
Add icon to spec file:
```python
exe = EXE(
    ...
    icon='resources/icon.ico',
)
```

## Troubleshooting Build Issues

### Missing Modules
Add to `hiddenimports` in spec file:
```python
hiddenimports=[
    'your_module_here',
],
```

### Large File Size
- Use UPX compression (enabled by default)
- Exclude unused modules
- Use directory build instead of --onefile

### Antivirus False Positives
- Sign the executable with a code signing certificate
- Submit to antivirus vendors for whitelisting
- Users may need to add exception

## GitHub Release Steps

1. Build: `python build.py`
2. Package: `python create_release.py`
3. Go to GitHub → Releases → Create New Release
4. Upload `release/YouTube-Downloader-Windows.zip`
5. Add release notes
6. Publish!
