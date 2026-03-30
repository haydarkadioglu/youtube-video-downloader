"""
Create a release package with the executable and necessary files
"""
import zipfile
import os
from pathlib import Path
import shutil

APP_VERSION = "v1.6.0"

def create_release():
    """Package the executable for distribution"""
    print("Creating release package...")
    
    # Paths
    dist_dir = Path("dist")
    exe_path = dist_dir / "yt-video-downloader.exe"
    release_dir = Path("release")
    
    # Check if exe exists
    if not exe_path.exists():
        print("✗ Executable not found. Run 'python build.py' first.")
        return
    
    # Create release directory
    release_dir.mkdir(exist_ok=True)
    
    # Create zip with version
    zip_name = release_dir / f"yt-video-downloader-{APP_VERSION}-windows.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add executable
        zipf.write(exe_path, "yt-video-downloader.exe")
        
        # Add README
        if Path("README.md").exists():
            zipf.write("README.md", "README.md")
        
        # Add LICENSE if exists
        if Path("LICENSE").exists():
            zipf.write("LICENSE", "LICENSE")
    
    print(f"✓ Release package created: {zip_name}")
    print(f"  Size: {zip_name.stat().st_size / 1024 / 1024:.1f} MB")
    print("\nReady to upload to GitHub Releases!")

if __name__ == "__main__":
    create_release()
