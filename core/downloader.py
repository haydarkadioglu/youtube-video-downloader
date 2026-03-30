import yt_dlp
from PyQt6.QtCore import QObject, pyqtSignal, QMutex, QWaitCondition
import os
from pathlib import Path
import time

class DownloadWorker(QObject):
    """Worker thread for downloading videos with pause/resume support"""
    
    progress = pyqtSignal(dict)
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)
    info_extracted = pyqtSignal(dict)
    paused = pyqtSignal()
    resumed = pyqtSignal()
    
    def __init__(self, url, output_path, quality, format_type):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.quality = quality
        self.format_type = format_type
        self.is_cancelled = False
        self.is_paused = False
        self.pause_mutex = QMutex()
        self.pause_condition = QWaitCondition()
    
    def cancel(self):
        """Cancel the download"""
        self.is_cancelled = True
        self.resume()  # Wake up if paused
    
    def pause(self):
        """Pause the download"""
        self.is_paused = True
        self.paused.emit()
    
    def resume(self):
        """Resume the download"""
        if self.is_paused:
            self.is_paused = False
            self.pause_condition.wakeAll()
            self.resumed.emit()
    
    def progress_hook(self, d):
        """Hook for download progress updates"""
        # Check for pause
        if self.is_paused:
            self.pause_mutex.lock()
            self.pause_condition.wait(self.pause_mutex)
            self.pause_mutex.unlock()
        
        # Check for cancel
        if self.is_cancelled:
            raise Exception("Download cancelled by user")
        
        if d['status'] == 'downloading':
            progress_info = {
                'status': 'downloading',
                'percent': d.get('_percent_str', '0%').strip(),
                'speed': d.get('_speed_str', 'N/A').strip(),
                'eta': d.get('_eta_str', 'N/A').strip(),
                'downloaded': d.get('_downloaded_bytes_str', '0B').strip(),
                'total': d.get('_total_bytes_str', 'Unknown').strip()
            }
            self.progress.emit(progress_info)
        
        elif d['status'] == 'finished':
            self.progress.emit({
                'status': 'processing',
                'percent': '100%',
                'speed': 'N/A',
                'eta': '0s'
            })
    
    def run(self):
        """Execute the download"""
        try:
            # Ensure output directory exists
            Path(self.output_path).mkdir(parents=True, exist_ok=True)
            
            # Determine local ffmpeg path
            from core.ffmpeg_utils import get_ffmpeg_dir
            ffmpeg_path = get_ffmpeg_dir()
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
                'ffmpeg_location': ffmpeg_path,
                'extractor_args': {'youtube': ['player_client=default']},
            }
            
            # Format selection based on user choice
            if self.format_type.lower() == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                })
            else:
                # Video format selection
                quality_map = {
                    '4K': 'bestvideo[height<=2160]+bestaudio/best',
                    '1080p': 'bestvideo[height<=1080]+bestaudio/best',
                    '720p': 'bestvideo[height<=720]+bestaudio/best',
                    '480p': 'bestvideo[height<=480]+bestaudio/best',
                    '360p': 'bestvideo[height<=360]+bestaudio/best',
                    'Best': 'bestvideo+bestaudio/best'
                }
                
                format_str = quality_map.get(self.quality, 'bestvideo+bestaudio/best')
                ydl_opts['format'] = format_str
                
                # Add post-processor for merging
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': self.format_type.lower(),
                }]
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if not self.is_cancelled:
                    info = ydl.extract_info(self.url, download=True)
                    
                    # Get the final filename
                    if self.format_type.lower() == 'mp3':
                        filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
                    else:
                        filename = ydl.prepare_filename(info)
                    
                    if not self.is_cancelled:
                        self.finished.emit(f"Download completed: {info.get('title', 'Unknown')}", filename)
        
        except Exception as e:
            if "cancelled by user" in str(e).lower():
                self.error.emit("Download cancelled")
            else:
                self.error.emit(f"Download failed: {str(e)}")


class VideoInfoExtractor(QObject):
    """Extract video information without downloading"""
    
    info_ready = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        """Extract video information"""
        try:
            # Determine local ffmpeg path
            from core.ffmpeg_utils import get_ffmpeg_dir
            ffmpeg_path = get_ffmpeg_dir()

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',
                'ffmpeg_location': ffmpeg_path,
                'extractor_args': {'youtube': ['player_client=default']},
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                if 'entries' in info:
                    # It's a playlist
                    playlist_info = {
                        'type': 'playlist',
                        'title': info.get('title', 'Unknown Playlist'),
                        'uploader': info.get('uploader', 'Unknown'),
                        'count': len(info['entries']),
                        'entries': info['entries']
                    }
                    self.info_ready.emit(playlist_info)
                else:
                    # Single video
                    formats = []
                    if 'formats' in info:
                        seen_heights = set()
                        for f in info['formats']:
                            height = f.get('height')
                            if height and height not in seen_heights:
                                formats.append({
                                    'quality': f"{height}p",
                                    'format': f.get('ext', 'mp4'),
                                    'filesize': f.get('filesize', 0)
                                })
                                seen_heights.add(height)
                    
                    video_info = {
                        'type': 'video',
                        'title': info.get('title', 'Unknown'),
                        'duration': info.get('duration', 0),
                        'thumbnail': info.get('thumbnail', ''),
                        'uploader': info.get('uploader', 'Unknown'),
                        'view_count': info.get('view_count', 0),
                        'formats': sorted(formats, key=lambda x: int(x['quality'][:-1]), reverse=True)
                    }
                    
                    self.info_ready.emit(video_info)
        
        except Exception as e:
            self.error.emit(f"Failed to extract video info: {str(e)}")
