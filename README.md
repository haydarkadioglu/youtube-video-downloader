# YouTube Video Downloader

<div align="center">

A professional, modern YouTube video downloader with a beautiful dark UI and persistent download queue.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

</div>

## ✨ Features

- **🎬 Video Downloads** - Download YouTube videos in multiple formats (MP4, WebM)
- **🎵 Audio Extraction** - Extract MP3 audio at 320kbps
- **📋 Playlist Support** - Download entire playlists with one click
- **⏯️ Queue Management** - Pause, resume, and cancel downloads individually
- **💾 Persistent Queue** - Downloads resume after app restart (SQLite database)
- **🎨 Modern UI** - Premium dark theme with soft gradients and smooth animations
- **⚡ Auto-Queue** - Downloads start automatically without blocking the UI
- **📊 Download History** - Track completed downloads
- **🔧 Custom Settings** - Configure quality, format, and download location

## 📸 Screenshots

### Main Download Tab
Clean, compact interface for adding videos to queue.

### Queue Tab
Manage active and pending downloads with individual controls.

## 🚀 Quick Start

### Option 1: Download Executable (Windows)
1. Download the latest release from [Releases](../../releases)
2. Extract the ZIP file
3. Run `yt-video-downloader.exe`
4. Done! No installation needed.

### Option 2: Run from Source

#### Prerequisites
- Python 3.8 or higher
- FFmpeg (for format conversion)

#### Installation

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/youtube-video-downloader.git
cd youtube-video-downloader
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Install FFmpeg**

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add to PATH or place in project folder

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo pacman -S ffmpeg    # Arch
```

**macOS:**
```bash
brew install ffmpeg
```

**4. Run the application**
```bash
python main.py
```

## 📖 Usage Guide

### Basic Download
1. Paste a YouTube URL in the input field
2. Click **Fetch** to load video info
3. Select format (MP4/WebM/MP3) and quality
4. Click **Add to Queue**
5. Switch to **Queue** tab to monitor progress

### Playlist Download
1. Paste a playlist URL
2. Click **Fetch**
3. All videos will be listed
4. Click **Add Playlist to Queue**
5. Videos download automatically

### Queue Controls
- **⏸ Pause** - Pause active download
- **▶ Resume** - Resume paused download
- **⏹ Cancel** - Stop and remove download

### Settings
- **Download Path** - Change save location via folder selector
- **Default Quality** - Set preferred quality in Settings tab
- **Auto-Start Queue** - Enable/disable automatic downloads on app start

## 🛠️ Building from Source

### Create Windows Executable

**1. Install PyInstaller**
```bash
pip install pyinstaller
```

**2. Build the executable**
```bash
pyinstaller youtube-downloader.spec
```

The executable will be in the `dist/` folder.

### Build Script (Alternative)
```bash
python build.py
```

## 📁 Project Structure

```
youtube-video-downloader/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── youtube-downloader.spec # PyInstaller configuration
├── core/
│   ├── config.py          # Settings manager
│   ├── database.py        # SQLite queue persistence
│   └── downloader.py      # yt-dlp wrapper
├── ui/
│   ├── main_window.py     # Main application window
│   ├── download_widget.py # URL input and video info
│   ├── queue_widget.py    # Download queue management
│   └── settings_widget.py # Application settings
└── resources/
    └── styles.qss         # Qt stylesheet (dark theme)
```

## 🗄️ Database

Download queue is stored in SQLite:
- **Location:** `~/.youtube-downloader/downloads.db`
- **Auto-created** on first run
- **Persistent** across app restarts
- **Tables:** downloads (id, title, url, format, quality, status, progress, etc.)

## ⚙️ Configuration

Settings saved in JSON:
- **Location:** `~/.youtube-downloader/config.json`
- **Editable** via Settings tab or manually

**Default Config:**
```json
{
    "download_path": "~/Downloads/YouTube",
    "default_quality": "1080p",
    "default_format": "mp4",
    "auto_start_queue": true,
    "max_simultaneous_downloads": 3
}
```

## 🐛 Troubleshooting

### "Download failed: HTTP Error 403"
- Update yt-dlp: `pip install --upgrade yt-dlp`
- YouTube frequently changes their API

### "FFmpeg not found"
- Ensure FFmpeg is installed and in PATH
- Alternative: Place `ffmpeg.exe` in app folder

### Downloads not resuming after restart
- Check database file exists: `~/.youtube-downloader/downloads.db`
- Enable "Auto-Start Queue" in settings

### Application won't start
- Check Python version: `python --version` (need 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## 🔄 Updates

Keep yt-dlp updated for best compatibility:
```bash
pip install --upgrade yt-dlp
```

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Credits

- **yt-dlp** - YouTube downloading engine
- **PyQt6** - GUI framework
- **FFmpeg** - Media processing

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## ⚠️ Disclaimer

This tool is for personal use only. Respect YouTube's Terms of Service and copyright laws. Download content you have permission to access.

---

<div align="center">
Made with ❤️ by [Your Name]
</div>
