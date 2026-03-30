"""
Simple build script for creating Windows executable
"""
import subprocess
import sys
import os

APP_NAME = "YT Video Downloader"
APP_VERSION = "v1.6.0"

def build():
    """Build the executable using PyInstaller"""
    print("=" * 60)
    print(f"{APP_NAME} {APP_VERSION} - Build Script")
    print("=" * 60)
    
    # Check if pyinstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("✗ PyInstaller not found")
        print("  Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")
    
    # Run PyInstaller
    print("\nBuilding executable...")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            ["pyinstaller", "youtube-downloader.spec", "--clean"],
            check=True,
            capture_output=False
        )
        
        print("-" * 60)
        print("✓ Build successful!")
        print(f"\n{APP_NAME} {APP_VERSION}")
        print("Executable location: dist/yt-video-downloader.exe")
        print("\nYou can now:")
        print("  1. Run: dist\\yt-video-downloader.exe")
        print("  2. Create a release ZIP with the exe")
        print("=" * 60)
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed with error code {e.returncode}")
        print("Check the output above for details")
        sys.exit(1)

if __name__ == "__main__":
    build()
