"""
Create a release package with the executable and necessary files
"""
import zipfile
import os
import urllib.request
import tempfile
from pathlib import Path

APP_VERSION = "v1.2.0"
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

def download_ffmpeg(cache_dir):
    """Download FFmpeg static build ZIP to a cache directory"""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    zip_path = cache_dir / "ffmpeg-windows.zip"
    
    if not zip_path.exists():
        print(f"Downloading FFmpeg from {FFMPEG_URL}...")
        try:
            req = urllib.request.Request(FFMPEG_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                total_size = int(response.info().get('Content-Length', 0))
                block_size = 1024 * 1024 # 1MB
                downloaded = 0
                while True:
                    data = response.read(block_size)
                    if not data:
                        break
                    out_file.write(data)
                    downloaded += len(data)
                    if total_size:
                        print(f"\rDownloaded {(downloaded/(1024*1024)):.1f}MB / {(total_size/(1024*1024)):.1f}MB", end="")
            print("\n✓ FFmpeg downloaded successfully.")
        except Exception as e:
            print(f"\n✗ Error downloading FFmpeg: {e}")
            if zip_path.exists():
                zip_path.unlink()
            return None
    else:
        print(f"✓ Using cached FFmpeg: {zip_path}")
        
    return zip_path

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
    
    # Download FFmpeg
    ffmpeg_zip_path = download_ffmpeg("build/cache")
    
    print(f"Packaging files into {zip_name}...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add executable
        zipf.write(exe_path, "yt-video-downloader.exe")
        
        # Add README
        if Path("README.md").exists():
            zipf.write("README.md", "README.md")
        
        # Add LICENSE if exists
        if Path("LICENSE").exists():
            zipf.write("LICENSE", "LICENSE")

        # Bundle FFmpeg binaries
        if ffmpeg_zip_path and ffmpeg_zip_path.exists():
            print("Adding FFmpeg binaries to package...")
            try:
                with zipfile.ZipFile(ffmpeg_zip_path, 'r') as fz:
                    for file_info in fz.infolist():
                        if file_info.filename.endswith('ffmpeg.exe') or file_info.filename.endswith('ffprobe.exe'):
                            bin_name = Path(file_info.filename).name
                            print(f"  Adding {bin_name}...")
                            with fz.open(file_info) as src, zipf.open(bin_name, 'w') as dest:
                                dest.write(src.read())
            except Exception as e:
                print(f"✗ Failed to extract FFmpeg binaries: {e}")
                print("Proceeding without FFmpeg...")
    
    print(f"✓ Release package created: {zip_name}")
    print(f"  Size: {zip_name.stat().st_size / 1024 / 1024:.1f} MB")
    print("\nReady to upload to GitHub Releases!")

if __name__ == "__main__":
    create_release()
