from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QMenuBar, QStatusBar, QMessageBox, QProgressDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from ui.download_widget import DownloadWidget
from ui.queue_widget import QueueWidget
from ui.settings_widget import SettingsDialog

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("YouTube Video Downloader")
        self.setMinimumSize(1000, 700)
        
        self.init_ui()
        self.create_menu_bar()
        self.create_status_bar()
        
        # Check requirements after window shows up
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.check_ffmpeg)
    
    def check_ffmpeg(self):
        """Check for and download FFmpeg if necessary"""
        from core.ffmpeg_utils import get_ffmpeg_dir, FFmpegSetupWorker
        from pathlib import Path
        
        bin_dir = Path(get_ffmpeg_dir())
        if (bin_dir / "ffmpeg.exe").exists() and (bin_dir / "ffprobe.exe").exists():
            return
            
        self.progress_dialog = QProgressDialog("Video motoru ayarlanıyor, lütfen bekleyin...", "İptal", 0, 100, self)
        self.progress_dialog.setWindowTitle("İlk Kurulum")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setCancelButton(None) # Disable cancel button
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        self.progress_dialog.show()
        
        self.ffmpeg_worker = FFmpegSetupWorker()
        self.ffmpeg_worker.progress.connect(self.progress_dialog.setValue)
        self.ffmpeg_worker.status.connect(self.progress_dialog.setLabelText)
        self.ffmpeg_worker.finished.connect(self.on_ffmpeg_finished)
        self.ffmpeg_worker.start()
        
    def on_ffmpeg_finished(self, success, message):
        """Handle FFmpeg setup completion"""
        self.progress_dialog.close()
        if not success:
            QMessageBox.warning(self, "Kurulum Uyarı", f"FFmpeg yüklenemedi: {message}\nBazı indirme/dönüştürme özellikleri çalışmayabilir.")
            
    def init_ui(self):
        """Initialize the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.West)
        
        # Download widget
        self.download_widget = DownloadWidget(self.config)
        self.tabs.addTab(self.download_widget, "📥 Download")
        
        # Queue widget with config for auto-queue management
        self.queue_widget = QueueWidget(self.config)
        self.tabs.addTab(self.queue_widget, "📋 Queue")
        
        # Connect download started signal to queue
        self.download_widget.download_started.connect(self.on_download_started)
        
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config, self)
        dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>YouTube Video Downloader</h2>
        <p>Version 1.0.0</p>
        <p>A modern, professional YouTube video downloader with Qt6 interface.</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Multiple quality options (4K, 1080p, 720p, etc.)</li>
            <li>MP3 audio extraction</li>
            <li>Download queue management</li>
            <li>Beautiful dark theme interface</li>
        </ul>
        <p>Built with PyQt6 and yt-dlp</p>
        """
        QMessageBox.about(self, "About", about_text)
    
    def on_download_started(self, download_info):
        """Handle download started"""
        self.queue_widget.add_download(download_info)
        self.status_bar.showMessage(f"Download started: {download_info['title']}")
