import json
import os
from pathlib import Path

class Config:
    """Configuration manager for the YouTube downloader application"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".youtube_downloader"
        self.config_file = self.config_dir / "config.json"
        self.default_config = {
            "download_path": str(Path.home() / "Downloads" / "YouTube"),
            "default_quality": "1080p",
            "default_format": "mp4",
            "theme": "dark",
            "max_simultaneous_downloads": 3,
            "auto_start_queue": True
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.config_file.exists():
            self.save_config(self.default_config)
            return self.default_config.copy()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # Merge with defaults to handle new keys
                config = self.default_config.copy()
                config.update(loaded_config)
                return config
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return self.default_config.copy()
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value and save"""
        self.config[key] = value
        self.save_config()
    
    def get_download_path(self):
        """Get download path and ensure it exists"""
        path = Path(self.get("download_path"))
        path.mkdir(parents=True, exist_ok=True)
        return str(path)
