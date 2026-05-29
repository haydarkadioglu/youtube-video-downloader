#!/usr/bin/env python3
"""
YouTube Downloader - CLI Edition
Otomatik video indirme + MP3 dönüşümü
"""

import os
import sys
import subprocess
import yt_dlp
from pathlib import Path

def download_media(url, output_dir="downloads", format_type="mp3", quality="best"):
    """Download and optionally convert to MP3"""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # FFmpeg kontrolü
    ffmpeg_path = "ffmpeg"
    try:
        subprocess.run([ffmpeg_path, "-version"], capture_output=True)
    except FileNotFoundError:
        print("[!] FFmpeg bulunamadı. yükleniyor...")
        install_ffmpeg()
    
    # yt-dlp options
    ydl_opts = {
        'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'ffmpeg_location': ffmpeg_path,
    }
    
    if format_type.lower() == "mp3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            # Force re-encode to avoid cut-off audio
            'postprocessor_args': ['-ss', '0', '-t', '99999'],  # No trimming
        })
    else:
        quality_map = {
            'best': 'bestvideo+bestaudio/best',
            '4k': 'bestvideo[height<=2160]+bestaudio/best',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best',
            '720p': 'bestvideo[height<=720]+bestaudio/best',
        }
        ydl_opts.update({
            'format': quality_map.get(quality.lower(), 'bestvideo+bestaudio/best'),
            'merge_output_format': 'mp4',
        })
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"[+] İndiriliyor: {url}")
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown')
            
            if format_type.lower() == 'mp3':
                final_path = output_dir / f"{title}.mp3"
            else:
                final_path = output_dir / f"{title}.mp4"
            
            print(f"[+] Tamamlandı: {final_path}")
            return str(final_path)
            
    except Exception as e:
        print(f"[!] Hata: {e}")
        return None

def download_playlist(url, output_dir="downloads", format_type="mp3"):
    """Download entire playlist"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ffmpeg_path = "ffmpeg"
    
    ydl_opts = {
        'outtmpl': str(output_dir / '%(playlist_title)s' / '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'ffmpeg_location': ffmpeg_path,
        'ignoreerrors': True,
    }
    
    if format_type.lower() == "mp3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        })
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"[+] Playlist indiriliyor: {url}")
            ydl.download([url])
            print(f"[+] Playlist tamamlandı -> {output_dir}")
    except Exception as e:
        print(f"[!] Hata: {e}")

def install_ffmpeg():
    """Install ffmpeg on Linux"""
    try:
        subprocess.run(["apt-get", "update", "-qq"], check=True)
        subprocess.run(["apt-get", "install", "-y", "-qq", "ffmpeg"], check=True)
        print("[+] FFmpeg yüklendi")
    except:
        print("[!] FFmpeg yüklenemedi elle kur: sudo apt install ffmpeg")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Downloader CLI")
    parser.add_argument("url", help="YouTube video/playlist URL")
    parser.add_argument("-f", "--format", choices=["mp3", "mp4", "webm"], default="mp3",
                       help="Çıktı formatı (default: mp3)")
    parser.add_argument("-q", "--quality", default="best",
                       help="Kalite (best, 4k, 1080p, 720p)")
    parser.add_argument("-o", "--output", default="downloads",
                       help="Çıktı dizini")
    parser.add_argument("--playlist", action="store_true",
                       help="Playlist modu")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"YouTube Downloader - CLI Edition")
    print(f"Format: {args.format} | Kalite: {args.quality}")
    print("=" * 60)
    
    if args.playlist:
        download_playlist(args.url, args.output, args.format)
    else:
        download_media(args.url, args.output, args.format, args.quality)
