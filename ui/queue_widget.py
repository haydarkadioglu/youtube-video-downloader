from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QGroupBox, QPushButton,
                             QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QThread
from core.downloader import DownloadWorker
import os
import subprocess
import platform

class DownloadItemWidget(QWidget):
    """Custom widget for each download item with controls"""
    
    def __init__(self, title, format_type, quality, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.parent_queue = parent
        self.init_ui(title, format_type, quality)
    
    def init_ui(self, title, format_type, quality):
        """Initialize item UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Top row: Title
        title_layout = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: 600; color: #fff; font-size: 10pt;")
        self.title_label.setWordWrap(True)
        title_layout.addWidget(self.title_label)
        layout.addLayout(title_layout)
        
        # Bottom row: Info + Controls
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)
        
        # Info text
        self.info_label = QLabel(f"Format: {format_type} | Quality: {quality} | Status: Pending...")
        self.info_label.setProperty("class", "info")
        self.info_label.setStyleSheet("color: #999; font-size: 8pt;")
        bottom_layout.addWidget(self.info_label, 1)
        
        # Control buttons
        self.pause_btn = QPushButton("⏸")
        self.pause_btn.setFixedSize(28, 24)
        self.pause_btn.setToolTip("Pause")
        self.pause_btn.clicked.connect(self.on_pause)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setProperty("class", "small")
        
        self.resume_btn = QPushButton("▶")
        self.resume_btn.setFixedSize(28, 24)
        self.resume_btn.setToolTip("Resume")
        self.resume_btn.clicked.connect(self.on_resume)
        self.resume_btn.setEnabled(False)
        self.resume_btn.setVisible(False)
        self.resume_btn.setProperty("class", "small")
        
        self.cancel_btn = QPushButton("⏹")
        self.cancel_btn.setFixedSize(28, 24)
        self.cancel_btn.setToolTip("Cancel")
        self.cancel_btn.clicked.connect(self.on_cancel)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setProperty("class", "small")
        
        bottom_layout.addWidget(self.pause_btn)
        bottom_layout.addWidget(self.resume_btn)
        bottom_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(bottom_layout)
        self.setLayout(layout)
        
        # Style the widget
        self.setStyleSheet("""
            DownloadItemWidget {
                background: rgba(40, 40, 45, 0.5);
                border: 1px solid rgba(60, 60, 65, 0.3);
                border-radius: 5px;
            }
        """)
    
    def enable_controls(self):
        """Enable pause and cancel buttons when download starts"""
        self.pause_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
    
    def disable_controls(self):
        """Disable all control buttons"""
        self.pause_btn.setEnabled(False)
        self.pause_btn.setVisible(True)
        self.resume_btn.setEnabled(False)
        self.resume_btn.setVisible(False)
        self.cancel_btn.setEnabled(False)
    
    def update_status(self, status_text):
        """Update info label"""
        parts = self.info_label.text().split('|')
        if len(parts) >= 2:
            self.info_label.setText(f"{parts[0]}| {parts[1]}| Status: {status_text}")
        else:
            self.info_label.setText(status_text)
    
    def on_pause(self):
        """Handle pause button click"""
        if self.parent_queue:
            self.parent_queue.pause_download(self.index)
            self.pause_btn.setVisible(False)
            self.resume_btn.setVisible(True)
            self.resume_btn.setEnabled(True)
    
    def on_resume(self):
        """Handle resume button click"""
        if self.parent_queue:
            self.parent_queue.resume_download(self.index)
            self.pause_btn.setVisible(True)
            self.resume_btn.setVisible(False)
    
    def on_cancel(self):
        """Handle cancel button click"""
        if self.parent_queue:
            self.parent_queue.cancel_download(self.index)
            self.disable_controls()


class QueueWidget(QWidget):
    """Download queue and history widget"""
    
    def __init__(self):
        super().__init__()
        self.downloads = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title = QLabel("Download Queue")
        title.setProperty("class", "title")
        layout.addWidget(title)
        
        # Queue Group
        queue_group = QGroupBox("Active & Completed")
        queue_layout = QVBoxLayout()
        queue_layout.setContentsMargins(8, 12, 8, 8)
        
        # List widget
        self.queue_list = QListWidget()
        self.queue_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        queue_layout.addWidget(self.queue_list)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear Completed")
        self.clear_btn.clicked.connect(self.clear_completed)
        self.clear_btn.setProperty("class", "secondary")
        
        self.open_folder_btn = QPushButton("Open Downloads Folder")
        self.open_folder_btn.clicked.connect(self.open_downloads_folder)
        self.open_folder_btn.setProperty("class", "secondary")
        
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.open_folder_btn)
        button_layout.addStretch()
        
        queue_layout.addLayout(button_layout)
        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)
        
        # Stats
        self.stats_label = QLabel("Total Downloads: 0 | Active: 0 | Completed: 0")
        self.stats_label.setProperty("class", "info")
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def start_download(self, index, config):
        """Start a download task for a specific item"""
        if 0 <= index < len(self.downloads):
            item_data = self.downloads[index]
            
            if item_data['status'] == 'downloading' and 'worker' in item_data:
                return

            # Create worker
            thread = QThread(self)
            worker = DownloadWorker(
                item_data['url'], 
                config.get_download_path(), 
                item_data['quality'], 
                item_data['format']
            )
            worker.moveToThread(thread)
            
            # Store references
            item_data['worker'] = worker
            item_data['thread'] = thread
            
            # Connect signals
            worker.finished.connect(lambda msg, path, idx=index: self.on_queue_download_finished(idx, msg, path))
            worker.error.connect(lambda err, idx=index: self.on_queue_download_error(idx, err))
            
            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.error.connect(thread.quit)
            
            # Enable controls on item widget
            item = self.queue_list.item(index)
            if item:
                widget = self.queue_list.itemWidget(item)
                if widget:
                    widget.enable_controls()
                    widget.update_status("Downloading...")
            
            thread.start()

    def pause_download(self, index):
        """Pause a download"""
        if 0 <= index < len(self.downloads):
            item_data = self.downloads[index]
            if 'worker' in item_data:
                item_data['worker'].pause()
                item = self.queue_list.item(index)
                if item:
                    widget = self.queue_list.itemWidget(item)
                    if widget:
                        widget.update_status("Paused")
    
    def resume_download(self, index):
        """Resume a paused download"""
        if 0 <= index < len(self.downloads):
            item_data = self.downloads[index]
            if 'worker' in item_data:
                item_data['worker'].resume()
                item = self.queue_list.item(index)
                if item:
                    widget = self.queue_list.itemWidget(item)
                    if widget:
                        widget.update_status("Resuming...")
    
    def cancel_download(self, index):
        """Cancel a download"""
        if 0 <= index < len(self.downloads):
            item_data = self.downloads[index]
            if 'worker' in item_data:
                item_data['worker'].cancel()
                item = self.queue_list.item(index)
                if item:
                    widget = self.queue_list.itemWidget(item)
                    if widget:
                        widget.update_status("Cancelling...")

    def on_queue_download_finished(self, index, message, path):
        """Handle finished download for queue item"""
        self.update_download_status(index, 'completed', path)
        
    def on_queue_download_error(self, index, error):
        """Handle error for queue item"""
        self.update_download_status(index, 'error')
        print(f"Error downloading item {index}: {error}")
        
    def add_download(self, info):
        """Add a download to the queue"""
        download_item = {
            'title': info['title'],
            'url': info['url'],
            'format': info['format'],
            'quality': info['quality'],
            'status': 'pending',
            'path': None
        }
        
        self.downloads.append(download_item)
        current_index = len(self.downloads) - 1
        
        # Create list item
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, current_index)
        self.queue_list.addItem(item)
        
        # Create custom widget for this item
        item_widget = DownloadItemWidget(
            info['title'],
            info['format'],
            info['quality'],
            current_index,
            self
        )
        
        item.setSizeHint(item_widget.sizeHint())
        self.queue_list.setItemWidget(item, item_widget)
        
        self.update_stats()
        
    def on_item_double_clicked(self, item):
        """Handle double click on item"""
        index = item.data(Qt.ItemDataRole.UserRole)
        if 0 <= index < len(self.downloads):
            download = self.downloads[index]
            if download['status'] == 'completed' and download['path']:
                folder = os.path.dirname(download['path'])
                if platform.system() == 'Windows':
                    subprocess.run(['explorer', '/select,', download['path']])
                elif platform.system() == 'Darwin':
                    subprocess.run(['open', '-R', download['path']])
                else:
                    subprocess.run(['xdg-open', folder])

    def update_download_status(self, index, status, file_path=None):
        """Update download status"""
        if 0 <= index < len(self.downloads):
            self.downloads[index]['status'] = status
            if file_path:
                self.downloads[index]['path'] = file_path
            
            item = self.queue_list.item(index)
            if item:
                widget = self.queue_list.itemWidget(item)
                if widget:
                    if status == 'completed':
                        widget.update_status("✅ Completed")
                        widget.disable_controls()
                    elif status == 'error':
                        widget.update_status("❌ Error")
                        widget.disable_controls()
            
            self.update_stats()
    
    def update_stats(self):
        """Update statistics"""
        total = len(self.downloads)
        active = sum(1 for d in self.downloads if d['status'] == 'downloading')
        completed = sum(1 for d in self.downloads if d['status'] == 'completed')
        
        self.stats_label.setText(f"Total: {total} | Active: {active} | Completed: {completed}")
    
    def clear_completed(self):
        """Clear completed downloads from the list"""
        for i in range(self.queue_list.count() - 1, -1, -1):
            item = self.queue_list.item(i)
            index = item.data(Qt.ItemDataRole.UserRole)
            if index < len(self.downloads) and self.downloads[index]['status'] == 'completed':
                self.queue_list.takeItem(i)
        
        self.downloads = [d for d in self.downloads if d['status'] != 'completed']
        self.update_stats()
    
    def open_downloads_folder(self):
        """Open the downloads folder in file explorer"""
        from core.config import Config
        config = Config()
        path = config.get_download_path()
        
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', path])
        else:
            subprocess.run(['xdg-open', path])
