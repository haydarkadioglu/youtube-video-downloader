import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class DownloadDatabase:
    """SQLite database manager for persistent download queue"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection"""
        if db_path is None:
            # Default location: user's home directory
            app_dir = Path.home() / '.youtube-downloader'
            app_dir.mkdir(exist_ok=True)
            db_path = str(app_dir / 'downloads.db')
        
        self.db_path = db_path
        self.connection = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create database and tables if they don't exist"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        cursor = self.connection.cursor()
        
        # Create downloads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                format TEXT NOT NULL,
                quality TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                file_path TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        # Create indices for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON downloads(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON downloads(created_at)')
        
        self.connection.commit()
    
    def add_download(self, title: str, url: str, format_type: str, quality: str) -> int:
        """Add a new download to the queue"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO downloads (title, url, format, quality, status)
            VALUES (?, ?, ?, ?, 'pending')
        ''', (title, url, format_type, quality))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def update_status(self, download_id: int, status: str, 
                     progress: Optional[int] = None, 
                     file_path: Optional[str] = None,
                     error_message: Optional[str] = None):
        """Update download status"""
        cursor = self.connection.cursor()
        
        updates = ['status = ?']
        params = [status]
        
        if progress is not None:
            updates.append('progress = ?')
            params.append(progress)
        
        if file_path is not None:
            updates.append('file_path = ?')
            params.append(file_path)
        
        if error_message is not None:
            updates.append('error_message = ?')
            params.append(error_message)
        
        if status == 'completed':
            updates.append('completed_at = CURRENT_TIMESTAMP')
        
        query = f"UPDATE downloads SET {', '.join(updates)} WHERE id = ?"
        params.append(download_id)
        
        cursor.execute(query, params)
        self.connection.commit()
    
    def get_pending_downloads(self) -> List[Dict]:
        """Get all pending or paused downloads"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM downloads 
            WHERE status IN ('pending', 'paused')
            ORDER BY created_at ASC
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_downloads(self) -> List[Dict]:
        """Get all downloads"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM downloads 
            ORDER BY created_at DESC
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """Get download history (completed and failed)"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM downloads 
            WHERE status IN ('completed', 'error')
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_download(self, download_id: int):
        """Delete a download from database"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM downloads WHERE id = ?', (download_id,))
        self.connection.commit()
    
    def clear_completed(self):
        """Remove all completed downloads from database"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM downloads WHERE status = ?', ('completed',))
        self.connection.commit()
    
    def cleanup_old_history(self, days: int = 30):
        """Delete history older than specified days"""
        cursor = self.connection.cursor()
        cursor.execute('''
            DELETE FROM downloads 
            WHERE status IN ('completed', 'error')
            AND datetime(created_at) < datetime('now', '-' || ? || ' days')
        ''', (days,))
        self.connection.commit()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
