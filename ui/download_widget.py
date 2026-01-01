from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QProgressBar,
                             QGroupBox, QMessageBox, QFileDialog, QSizePolicy)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from core.downloader import VideoInfoExtractor
import requests

class DownloadWidget(QWidget):
    """Main download interface widget - Auto-queuing mode"""
    
    download_started = pyqtSignal(dict)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.video_info = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize compact professional UI"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Title - Minimal
        title = QLabel("YouTube Downloader")
        title.setProperty("class", "title")
        layout.addWidget(title)
        
        # URL Input Row
        url_layout = QHBoxLayout()
        url_layout.setSpacing(6)
        
        url_label = QLabel("URL:")
        url_label.setProperty("class", "section")
        url_label.setFixedWidth(35)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://youtube.com/watch?v=...")
        self.url_input.returnPressed.connect(self.fetch_video_info)
        self.url_input.textChanged.connect(self.on_url_changed)
        
        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.clicked.connect(self.fetch_video_info)
        self.fetch_btn.setFixedWidth(70)
        self.fetch_btn.setProperty("class", "secondary")
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.fetch_btn)
        layout.addLayout(url_layout)
        
        # Info Display - Compact
        self.info_widget = QWidget()
        self.info_widget.setVisible(False)
        info_layout = QHBoxLayout(self.info_widget)
        info_layout.setContentsMargins(0, 4, 0, 4)
        info_layout.setSpacing(8)
        
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(120, 68)
        self.thumbnail_label.setScaledContents(True)
        self.thumbnail_label.setStyleSheet("border: 1px solid #3a3a3a; border-radius: 4px;")
        info_layout.addWidget(self.thumbnail_label)
        
        info_text_layout = QVBoxLayout()
        info_text_layout.setSpacing(2)
        
        self.title_label = QLabel()
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-weight: 600; color: #fff;")
        
        self.meta_label = QLabel()
        self.meta_label.setProperty("class", "info")
        
        info_text_layout.addWidget(self.title_label)
        info_text_layout.addWidget(self.meta_label)
        info_text_layout.addStretch()
        
        info_layout.addLayout(info_text_layout, 1)
        layout.addWidget(self.info_widget)
        
        # Download Options - Single Compact Row
        options_group = QGroupBox("Options")
        options_layout = QHBoxLayout()
        options_layout.setSpacing(8)
        options_layout.setContentsMargins(8, 12, 8, 8)
        
        # Format
        format_layout = QVBoxLayout()
        format_layout.setSpacing(3)
        format_label = QLabel("Format")
        format_label.setProperty("class", "info")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "WebM", "MP3"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        options_layout.addLayout(format_layout)
        
        # Quality
        quality_layout = QVBoxLayout()
        quality_layout.setSpacing(3)
        quality_label = QLabel("Quality")
        quality_label.setProperty("class", "info")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Best", "4K", "1080p", "720p", "480p", "360p"])
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)
        options_layout.addLayout(quality_layout)
        
        # Folder
        folder_layout = QVBoxLayout()
        folder_layout.setSpacing(3)
        folder_label = QLabel("Save to")
        folder_label.setProperty("class", "info")
        
        folder_row = QHBoxLayout()
        folder_row.setSpacing(4)
        self.path_input = QLineEdit(self.config.get_download_path())
        self.path_input.setReadOnly(True)
        self.path_input.setStyleSheet("font-size: 8pt;")
        
        self.browse_btn = QPushButton("...")
        self.browse_btn.setFixedWidth(30)
        self.browse_btn.clicked.connect(self.browse_download_path)
        self.browse_btn.setProperty("class", "secondary small")
        
        folder_row.addWidget(self.path_input)
        folder_row.addWidget(self.browse_btn)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addLayout(folder_row)
        options_layout.addLayout(folder_layout, 1)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Primary Button - Add to Queue
        self.download_btn = QPushButton("Add to Queue")
        self.download_btn.setMinimumHeight(36)
        self.download_btn.clicked.connect(self.add_to_queue)
        self.download_btn.setEnabled(False)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background: #0e639c;
                font-size: 11pt;
                font-weight: 700;
                border-radius: 4px;
            }
            QPushButton:hover:enabled {
                background: #1177bb;
            }
            QPushButton:disabled {
                background: #3a3a3a;
                color: #666;
            }
        """)
        layout.addWidget(self.download_btn)
        
        # Status
        self.status_label = QLabel("Ready - Enter a YouTube URL to begin")
        self.status_label.setProperty("class", "info")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        self.setLayout(layout)
        self.on_format_changed("MP4")
    
    def on_url_changed(self, text):
        """Enable fetch when URL is present"""
        has_url = len(text.strip()) > 10
        self.fetch_btn.setEnabled(has_url)
    
    def on_format_changed(self, format_text):
        """Handle format change"""
        if format_text == "MP3":
            self.quality_combo.setEnabled(False)
            self.quality_combo.setCurrentText("Best")
        else:
            self.quality_combo.setEnabled(True)
    
    def browse_download_path(self):
        """Browse for download folder"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Download Folder", self.config.get_download_path()
        )
        if dir_path:
            self.config.set("download_path", dir_path)
            self.path_input.setText(dir_path)
    
    def fetch_video_info(self):
        """Fetch video/playlist information"""
        url = self.url_input.text().strip()
        if not url:
            return
        
        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("...")
        self.status_label.setText("Fetching info...")
        
        self.info_thread = QThread()
        self.info_worker = VideoInfoExtractor(url)
        self.info_worker.moveToThread(self.info_thread)
        
        self.info_thread.started.connect(self.info_worker.run)
        self.info_worker.info_ready.connect(self.on_info_ready)
        self.info_worker.error.connect(self.on_info_error)
        self.info_worker.info_ready.connect(self.info_thread.quit)
        self.info_worker.error.connect(self.info_thread.quit)
        self.info_thread.finished.connect(self.info_thread.deleteLater)
        
        self.info_thread.start()
    
    def on_info_ready(self, info):
        """Handle fetched info"""
        self.video_info = info
        
        if info.get('type') == 'playlist':
            self.title_label.setText(f"🎵 {info['title']}")
            self.meta_label.setText(f"{info['count']} videos • {info['uploader']}")
            self.thumbnail_label.setText("Playlist")
            self.download_btn.setText(f"Add Playlist to Queue ({info['count']} videos)")
        else:
            self.title_label.setText(info['title'])
            duration = info['duration']
            mins, secs = divmod(duration, 60)
            
            # Get format info
            format_info = ""
            if info.get('formats') and len(info['formats']) > 0:
                best_format = info['formats'][0]
                filesize = best_format.get('filesize', 0)
                if filesize > 0:
                    size_mb = filesize / (1024 * 1024)
                    if size_mb >= 1024:
                        format_info = f" • ~{size_mb/1024:.1f}GB"
                    else:
                        format_info = f" • ~{size_mb:.0f}MB"
            
            self.meta_label.setText(f"{mins}:{secs:02d} • {info['uploader']}{format_info}")
            
            if info['thumbnail']:
                try:
                    response = requests.get(info['thumbnail'], timeout=5)
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    self.thumbnail_label.setPixmap(pixmap)
                except:
                    pass
            
            self.download_btn.setText("Add to Queue")
        
        self.info_widget.setVisible(True)
        self.download_btn.setEnabled(True)
        self.status_label.setText("Ready to add to queue")
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch")
    
    def on_info_error(self, error):
        """Handle fetch error"""
        self.status_label.setText(f"Error: {error}")
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch")
        QMessageBox.critical(self, "Error", error)
    
    def add_to_queue(self):
        """Add download(s) to queue"""
        if not self.video_info:
            QMessageBox.warning(self, "Error", "Please fetch video info first")
            return
        
        quality = self.quality_combo.currentText()
        format_type = self.format_combo.currentText()
        
        if self.video_info.get('type') == 'playlist':
            count = 0
            playlist_name = self.video_info.get('title', 'Playlist')
            for entry in self.video_info['entries']:
                if entry:
                    url = entry.get('url') or entry.get('original_url')
                    if not url and entry.get('id'):
                        url = f"https://www.youtube.com/watch?v={entry['id']}"
                    
                    if url:
                        self.download_started.emit({
                            'title': entry.get('title', 'Unknown'),
                            'url': url,
                            'format': format_type,
                            'quality': quality,
                            'is_playlist_item': True,
                            'playlist_name': playlist_name
                        })
                        count += 1
            
            QMessageBox.information(self, "Queued", 
                f"Added {count} videos to queue.\nGo to Queue tab to monitor progress.")
            
        else:
            url = self.url_input.text().strip()
            
            self.download_started.emit({
                'title': self.video_info['title'],
                'url': url,
                'format': format_type,
                'quality': quality
            })
            
            QMessageBox.information(self, "Queued", 
                f"'{self.video_info['title']}' added to queue.\nDownload will start automatically.")
        
        # Reset UI
        self.video_info = None
        self.info_widget.setVisible(False)
        self.download_btn.setEnabled(False)
        self.download_btn.setText("Add to Queue")
        self.url_input.clear()
        self.status_label.setText("Ready - Enter a YouTube URL to begin")
