import os
import sys
import urllib.request
import zipfile
import tempfile
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"

def get_ffmpeg_dir():
    """Determine the local directory path for ffmpeg within the app's context."""
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, "bin")

class FFmpegSetupWorker(QThread):
    """Background worker to download and extract FFmpeg"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str) # success, message
    
    def run(self):
        try:
            bin_dir = Path(get_ffmpeg_dir())
            ffmpeg_exe = bin_dir / "ffmpeg.exe"
            ffprobe_exe = bin_dir / "ffprobe.exe"
            
            # Already exists?
            if ffmpeg_exe.exists() and ffprobe_exe.exists():
                self.progress.emit(100)
                self.status.emit("Sistem hazır.")
                self.finished.emit(True, "FFmpeg sistemde mevcut.")
                return
                
            self.status.emit("Video dönüştürücü motor yükleniyor (0 MB / 40 MB)...")
            self.progress.emit(0)
            
            bin_dir.mkdir(parents=True, exist_ok=True)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = Path(temp_dir) / "ffmpeg.zip"
                
                # Downloading
                req = urllib.request.Request(FFMPEG_URL, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                    total_size = int(response.info().get('Content-Length', 0))
                    block_size = 1024 * 512 # 512 KB
                    downloaded = 0
                    
                    while True:
                        data = response.read(block_size)
                        if not data:
                            break
                        out_file.write(data)
                        downloaded += len(data)
                        
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 85) # Reserving 15% for extraction
                            dl_mb = downloaded / (1024*1024)
                            tot_mb = total_size / (1024*1024)
                            self.status.emit(f"Dönüştürücü motor yükleniyor ({dl_mb:.1f} MB / {tot_mb:.1f} MB)...")
                            self.progress.emit(percent)
                
                # Extracting
                self.status.emit("Dosyalar diske çıkartılıyor, lütfen bekleyin...")
                self.progress.emit(85)
                
                with zipfile.ZipFile(zip_path, 'r') as fz:
                    for file_info in fz.infolist():
                        if file_info.filename.endswith('ffmpeg.exe') or file_info.filename.endswith('ffprobe.exe'):
                            bin_name = Path(file_info.filename).name
                            with fz.open(file_info) as src, open(bin_dir / bin_name, 'wb') as dest:
                                dest.write(src.read())
                                
                self.progress.emit(100)
                self.status.emit("Yükleme tamamlandı!")
                self.finished.emit(True, "Kurulum başarılı.")
                
        except Exception as e:
            self.finished.emit(False, str(e))
