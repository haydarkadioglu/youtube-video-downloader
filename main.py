"""
YouTube Video Downloader
A modern Qt6 application for downloading YouTube videos in various formats and qualities
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from core.config import Config
from ui.main_window import MainWindow

def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Video Downloader")
    app.setOrganizationName("YTDownloader")
    
    # Load configuration
    config = Config()
    
    # Load stylesheet
    try:
        with open('resources/styles.qss', 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Warning: Could not load stylesheet")
    
    # Create and show main window
    window = MainWindow(config)
    window.show()
    
    # Close splash screen if running from PyInstaller bundle
    try:
        import pyi_splash
        pyi_splash.close()
    except ImportError:
        pass
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
