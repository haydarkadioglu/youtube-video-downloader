from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QMenuBar, QStatusBar, QMessageBox)
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
