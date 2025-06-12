#!/usr/bin/env python3
"""
Expansion Progress Monitor

Monitor the progress of the collection expansion without interrupting the process.
Shows real-time statistics about the expansion progress.

Usage:
    python monitor_expansion.py

Author: MusicTool MVP  
Created: June 12, 2025
"""

import sqlite3
import pandas as pd
import time
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))

from core.discogs_parser import DiscogsCSVParser


def get_current_progress():
    """Get current expansion progress from database."""
    try:
        # Connect to database
        conn = sqlite3.connect('./data/musictool.db')
        
        # Get expanded tracks
        tracks_df = pd.read_sql('SELECT * FROM expanded_tracks', conn)
        conn.close()
        
        if len(tracks_df) == 0:
            return 0, 0, []
        
        unique_releases = tracks_df['discogs_release_id'].nunique()
        total_tracks = len(tracks_df)
        
        # Get recent releases (last 5)
        recent_releases = tracks_df.groupby('discogs_release_id').agg({
            'artist': 'first',
            'album': 'first', 
            'created_at': 'first'
        }).sort_values('created_at', ascending=False).head(5)
        
        return unique_releases, total_tracks, recent_releases
        
    except Exception as e:
        print(f"Error reading database: {e}")
        return 0, 0, []


def get_total_releases():
    """Get total number of releases to process."""
    try:
        parser = DiscogsCSVParser('./data/gazmazk4ez-collection-20250608-1029.csv')
        all_releases = parser.parse()
        return len(all_releases)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return 598  # fallback


def main():
    """Monitor expansion progress."""
    total_releases = get_total_releases()
    start_time = datetime.now()
    last_count = 0
    
    print("🎵 MusicTool Collection Expansion Monitor")
    print("=" * 50)
    print(f"📊 Total releases to process: {total_releases}")
    print(f"⏰ Started monitoring at: {start_time.strftime('%H:%M:%S')}")
    print("\nPress Ctrl+C to stop monitoring\n")
    
    try:
        while True:
            current_releases, current_tracks, recent = get_current_progress()
            
            # Calculate progress
            progress_pct = (current_releases / total_releases) * 100
            remaining = total_releases - current_releases
            
            # Calculate rate
            now = datetime.now()
            elapsed = (now - start_time).total_seconds()
            releases_added = current_releases - last_count if last_count > 0 else 0
            
            if elapsed > 0:
                rate = current_releases / elapsed * 60  # releases per minute
                if rate > 0:
                    eta_minutes = remaining / (rate / 60)
                    eta_time = now + pd.Timedelta(minutes=eta_minutes)
                    eta_str = eta_time.strftime('%H:%M:%S')
                else:
                    eta_str = "calculating..."
            else:
                eta_str = "calculating..."
                rate = 0
            
            # Print status
            print(f"\r🚀 Progress: {current_releases:3d}/{total_releases} ({progress_pct:5.1f}%) | "
                  f"Tracks: {current_tracks:4d} | "
                  f"Rate: {rate:4.1f}/min | "
                  f"ETA: {eta_str}", end="")
            
            # Show recent releases every 30 seconds
            if int(elapsed) % 30 == 0 and len(recent) > 0:
                print(f"\n\n📀 Recently expanded:")
                for release_id, row in recent.iterrows():
                    print(f"   → {release_id}: {row['artist']} - {row['album']}")
                print()
            
            last_count = current_releases
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print(f"\n\n⏹️ Monitoring stopped")
        print(f"📊 Final stats: {current_releases}/{total_releases} releases ({progress_pct:.1f}%)")
        print(f"🎵 Total tracks: {current_tracks}")


if __name__ == "__main__":
    main()
