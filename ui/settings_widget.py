from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QFileDialog, QGroupBox,
                             QMessageBox)
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    """Settings dialog for application configuration"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Settings")
        title.setProperty("class", "title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Download Settings Group
        download_group = QGroupBox("Download Settings")
        download_layout = QVBoxLayout()
        
        # Default quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Default Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Best", "4K", "1080p", "720p", "480p", "360p"])
        current_quality = self.config.get("default_quality", "1080p")
        self.quality_combo.setCurrentText(current_quality)
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        download_layout.addLayout(quality_layout)
        
        # Default format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Default Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "webm", "mp3"])
        current_format = self.config.get("default_format", "mp4")
        self.format_combo.setCurrentText(current_format)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        download_layout.addLayout(format_layout)
        
        # Download path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Download Path:"))
        self.path_label = QLabel(self.config.get_download_path())
        self.path_label.setStyleSheet("color: #60a5fa; padding: 8px;")
        self.path_label.setWordWrap(True)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setMaximumWidth(100)
        self.browse_btn.clicked.connect(self.browse_path)
        
        path_layout.addWidget(self.path_label, 1)
        path_layout.addWidget(self.browse_btn)
        download_layout.addLayout(path_layout)
        
        download_group.setLayout(download_layout)
        layout.addWidget(download_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setProperty("class", "secondary")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_path(self):
        """Browse for download path"""
        dir_path = QFileDialog.getExistingDirectory(
            self, 
            "Select Download Directory",
            self.config.get_download_path()
        )
        if dir_path:
            self.path_label.setText(dir_path)
    
    def save_settings(self):
        """Save settings to config"""
        self.config.set("default_quality", self.quality_combo.currentText())
        self.config.set("default_format", self.format_combo.currentText())
        self.config.set("download_path", self.path_label.text())
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")
        self.accept()
