"""
Collection Expander

Expands Discogs releases into individual tracks by fetching tracklists
from the Discogs API and creating a unified physical collection database.

Author: MusicTool MVP
Created: June 12, 2025
"""

import pandas as pd
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

from .discogs_client import DiscogsAPIClient, load_api_key_from_env
from .discogs_parser import DiscogsCSVParser

logger = logging.getLogger(__name__)


class CollectionExpander:
    """Expands Discogs releases into individual tracks and manages the physical collection database."""
    
    def __init__(self, api_key: str, db_path: str = "./data/musictool.db"):
        """
        Initialize the Collection Expander.
        
        Args:
            api_key: Discogs API key
            db_path: Path to SQLite database for storing expanded collection
        """
        self.api_client = DiscogsAPIClient(api_key)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Collection Expander initialized with database: {db_path}")
    
    def expand_collection(self, discogs_csv_path: str, max_releases: int = None, skip_existing: bool = True) -> pd.DataFrame:
        """
        Expand a Discogs collection CSV into individual tracks.
        
        Args:
            discogs_csv_path: Path to Discogs CSV export
            max_releases: Maximum number of releases to process (None for all)
            skip_existing: Skip releases already in database
            
        Returns:
            DataFrame with expanded track collection
        """
        logger.info(f"Starting collection expansion")
        
        # Parse Discogs CSV
        parser = DiscogsCSVParser(discogs_csv_path)
        releases_df = parser.parse()
        
        total_releases = len(releases_df)
        logger.info(f"Found {total_releases} releases in CSV")
        
        # Get releases to process
        if skip_existing:
            already_expanded = self._get_expanded_release_ids()
            releases_to_process = releases_df[~releases_df['release_id'].isin(already_expanded)]
            logger.info(f"Skipping {len(already_expanded)} already expanded releases")
        else:
            releases_to_process = releases_df
        
        if max_releases:
            releases_to_process = releases_to_process.head(max_releases)
            logger.info(f"Limited to {max_releases} releases")
        
        release_ids = releases_to_process['release_id'].tolist()
        logger.info(f"Processing {len(release_ids)} releases")
        
        # Track progress
        expanded_tracks = []
        processed = 0
        errors = 0
        
        for i, release_id in enumerate(release_ids):
            try:
                logger.info(f"Processing release {i+1}/{len(release_ids)}: {release_id}")
                
                # Get release info from CSV
                release_info = releases_df[releases_df['release_id'] == release_id].iloc[0]
                logger.info(f"  → {release_info['artist_clean']} - {release_info['title']}")
                
                # Get tracklist from API
                tracklist = self.api_client.get_release_tracklist(release_id)
                
                if tracklist:
                    track_count = len([t for t in tracklist if t['type_'] == 'track'])
                    
                    if track_count > 0:
                        # Convert tracks to expanded format
                        release_tracks = []
                        for track in tracklist:
                            if track['type_'] == 'track':  # Skip headings, etc.
                                expanded_track = self._create_expanded_track(track, release_info)
                                release_tracks.append(expanded_track)
                        
                        # Save this release immediately (for crash recovery)
                        release_df = pd.DataFrame(release_tracks)
                        self._save_expanded_collection(release_df)
                        
                        expanded_tracks.extend(release_tracks)
                        processed += 1
                        logger.info(f"  ✅ {track_count} tracks added and saved to database")
                    else:
                        logger.warning(f"  ⚠️ No actual tracks found (only headings/metadata)")
                        processed += 1
                else:
                    logger.warning(f"  ❌ No tracklist found for release {release_id}")
                    errors += 1
                    
                # Progress update every 10 releases
                if (i + 1) % 10 == 0:
                    logger.info(f"📊 Progress: {i+1}/{len(release_ids)} releases processed ({processed} successful, {errors} errors)")
                    
            except KeyboardInterrupt:
                logger.info("⏹️ Interrupted by user")
                break
            except Exception as e:
                logger.error(f"  ❌ Error processing release {release_id}: {e}")
                errors += 1
                continue
        
        # Final summary
        logger.info(f"🎉 Expansion complete!")
        logger.info(f"📊 Final stats: {processed} successful, {errors} errors out of {len(release_ids)} total")
        
        # Return full collection
        return self.load_physical_collection()
    
    def _create_expanded_track(self, track: Dict[str, Any], release_info: pd.Series) -> Dict[str, Any]:
        """Create an expanded track record combining track and release info."""
        
        # Extract artist - prefer track artists, fallback to release artist
        track_artists = track.get('artists', [])
        if track_artists:
            artist = ', '.join(track_artists)
        else:
            artist = release_info['artist_clean']
        
        # Create unified track record
        expanded_track = {
            # Core track info
            'artist': artist,
            'title': track['title'],
            'position': track['position'],
            'duration': track['duration'],
            
            # Release/album info
            'album': release_info['title'],
            'album_artist': release_info['artist_clean'],
            'label': release_info['label'],
            'catalog_number': release_info['catalog_number_clean'],
            'release_year': release_info['release_year'],
            'format_type': release_info['format_type'],
            'format_description': release_info['format_description'],
            
            # Collection metadata
            'collection_folder': release_info['collection_folder'],
            'date_added': release_info['date_added'],
            'media_condition': release_info['media_condition'],
            'sleeve_condition': release_info['sleeve_condition'],
            'notes': release_info['notes'],
            
            # Source tracking
            'discogs_release_id': release_info['release_id'],
            'source': 'discogs_physical',
            'expanded_date': datetime.now().isoformat()
        }
        
        return expanded_track
    
    def _init_database(self):
        """Initialize SQLite database for storing expanded collection."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create expanded tracks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expanded_tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    artist TEXT NOT NULL,
                    title TEXT NOT NULL,
                    position TEXT,
                    duration TEXT,
                    album TEXT,
                    album_artist TEXT,
                    label TEXT,
                    catalog_number TEXT,
                    release_year INTEGER,
                    format_type TEXT,
                    format_description TEXT,
                    collection_folder TEXT,
                    date_added TEXT,
                    media_condition TEXT,
                    sleeve_condition TEXT,
                    notes TEXT,
                    discogs_release_id INTEGER,
                    source TEXT,
                    expanded_date TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_artist_title 
                ON expanded_tracks(artist, title)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_release_id 
                ON expanded_tracks(discogs_release_id)
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def _get_expanded_release_ids(self) -> List[int]:
        """Get list of release IDs that have already been expanded."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT discogs_release_id FROM expanded_tracks')
                release_ids = [row[0] for row in cursor.fetchall()]
                logger.info(f"Found {len(release_ids)} already expanded releases")
                return release_ids
        except Exception as e:
            logger.warning(f"Error getting expanded release IDs: {e}")
            return []
    
    def _save_expanded_collection(self, df: pd.DataFrame):
        """Save expanded collection to SQLite database."""
        if df.empty:
            logger.warning("No tracks to save")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            # Clear existing data for these releases
            release_ids = df['discogs_release_id'].unique().tolist()
            placeholders = ','.join(['?' for _ in release_ids])
            
            cursor = conn.cursor()
            cursor.execute(f'''
                DELETE FROM expanded_tracks 
                WHERE discogs_release_id IN ({placeholders})
            ''', release_ids)
            
            # Insert new data
            df.to_sql('expanded_tracks', conn, if_exists='append', index=False)
            
            logger.info(f"Saved {len(df)} tracks to database")
    
    def load_physical_collection(self) -> pd.DataFrame:
        """Load the expanded physical collection from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query('SELECT * FROM expanded_tracks', conn)
                logger.info(f"Loaded {len(df)} tracks from physical collection database")
                return df
        except Exception as e:
            logger.error(f"Error loading physical collection: {e}")
            return pd.DataFrame()
    
    def get_expansion_stats(self) -> Dict[str, Any]:
        """Get statistics about the expanded collection."""
        df = self.load_physical_collection()
        
        if df.empty:
            return {'total_tracks': 0, 'total_releases': 0}
        
        stats = {
            'total_tracks': len(df),
            'total_releases': df['discogs_release_id'].nunique(),
            'unique_artists': df['artist'].nunique(),
            'unique_albums': df['album'].nunique(),
            'format_breakdown': df['format_type'].value_counts().to_dict(),
            'collection_folders': df['collection_folder'].value_counts().to_dict(),
            'labels': df['label'].nunique(),
            'year_range': {
                'earliest': int(df['release_year'].min()) if df['release_year'].min() > 0 else None,
                'latest': int(df['release_year'].max()) if df['release_year'].max() > 0 else None
            }
        }
        
        return stats


def expand_collection_cli(csv_path: str, max_releases: int = 10):
    """Command-line interface for collection expansion."""
    api_key = load_api_key_from_env()
    if not api_key:
        print("❌ No Discogs API key found in .env file")
        return None
    
    expander = CollectionExpander(api_key)
    
    print(f"🚀 Starting collection expansion (max {max_releases} releases)")
    expanded_df = expander.expand_collection(csv_path, max_releases)
    
    if not expanded_df.empty:
        print(f"\n✅ Expansion complete!")
        stats = expander.get_expansion_stats()
        print(f"📊 Results: {stats['total_tracks']} tracks from {stats['total_releases']} releases")
        print(f"🎵 Artists: {stats['unique_artists']}, Albums: {stats['unique_albums']}")
        return expanded_df
    else:
        print("❌ No tracks expanded")
        return None


if __name__ == "__main__":
    # Quick test
    import sys
    max_releases = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    
    csv_path = "./data/gazmazk4ez-collection-20250608-1029.csv"
    expand_collection_cli(csv_path, max_releases)
