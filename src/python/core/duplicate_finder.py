"""
Digital Collection Duplicate Finder

Identifies potential duplicate tracks in digital music collections using fuzzy matching.
Helpful for cleaning up collections with slight variations in track names, artists, or metadata.

Author: MusicTool MVP
Created: June 12, 2025
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional, Set
import logging
from fuzzywuzzy import fuzz
import re
from collections import defaultdict
import time

from .nml_parser import NMLParser

logger = logging.getLogger(__name__)


class DuplicateFinder:
    """Finds potential duplicate tracks in digital music collections."""
    
    def __init__(self, nml_path: str):
        """
        Initialize the Duplicate Finder.
        
        Args:
            nml_path: Path to NML file (digital collection)
        """
        self.nml_path = nml_path
        self.digital_collection = self._load_digital_collection()
        
        logger.info(f"Duplicate Finder initialized with {len(self.digital_collection)} tracks")
    
    def find_duplicates(self, similarity_threshold: int = 85, group_by: str = "artist_title") -> pd.DataFrame:
        """
        Find potential duplicate tracks in the digital collection.
        
        Args:
            similarity_threshold: Minimum similarity score to consider tracks duplicates (0-100)
            group_by: Method for grouping potential duplicates:
                     - "artist_title": Group by artist and title similarity
                     - "title_only": Group by title similarity only
                     - "filename": Group by filename similarity
                     - "duration": Group by similar duration and title
            
        Returns:
            DataFrame with duplicate groups and similarity scores
        """
        logger.info(f"Starting duplicate search (threshold: {similarity_threshold}%, method: {group_by})")
        start_time = time.time()
        
        if self.digital_collection.empty:
            logger.warning("No digital collection data found")
            return pd.DataFrame()
        
        duplicate_groups = []
        processed_tracks = set()
        
        # Process each track
        for idx, track in self.digital_collection.iterrows():
            if idx in processed_tracks:
                continue
                
            # Find similar tracks
            similar_tracks = self._find_similar_tracks(
                track, idx, similarity_threshold, group_by, processed_tracks
            )
            
            if similar_tracks:
                # Create duplicate group
                group_id = len(duplicate_groups) + 1
                
                # Add the original track
                duplicate_groups.append(self._create_duplicate_record(track, idx, group_id, 1, 100.0, "original"))
                
                # Add similar tracks
                for similar_track, similar_idx, similarity_score in similar_tracks:
                    duplicate_groups.append(
                        self._create_duplicate_record(
                            similar_track, similar_idx, group_id, 
                            len([t for t in similar_tracks if t[2] >= similarity_score]) + 2,
                            similarity_score, "duplicate"
                        )
                    )
                    processed_tracks.add(similar_idx)
                
                processed_tracks.add(idx)
        
        # Convert to DataFrame
        duplicates_df = pd.DataFrame(duplicate_groups)
        
        # Add summary statistics
        elapsed_time = time.time() - start_time
        total_groups = duplicates_df['group_id'].nunique() if not duplicates_df.empty else 0
        total_duplicates = len(duplicates_df) if not duplicates_df.empty else 0
        
        logger.info(f"🔍 Duplicate search complete:")
        logger.info(f"  Processing time: {elapsed_time:.2f}s")
        logger.info(f"  Duplicate groups found: {total_groups}")
        logger.info(f"  Total duplicate tracks: {total_duplicates}")
        
        return duplicates_df
    
    def _find_similar_tracks(self, reference_track: pd.Series, ref_idx: int, 
                           threshold: int, method: str, processed: Set[int]) -> List[Tuple]:
        """Find tracks similar to the reference track."""
        similar_tracks = []
        
        # Normalize reference track data
        ref_artist = self._normalize_text(reference_track['artist'])
        ref_title = self._normalize_text(reference_track['title'])
        ref_filename = self._normalize_filename(reference_track.get('location', ''))
        ref_duration = reference_track.get('totaltime', 0)
        
        # Search through remaining tracks
        for idx, track in self.digital_collection.iterrows():
            if idx <= ref_idx or idx in processed:
                continue
            
            # Calculate similarity based on method
            similarity_score = self._calculate_similarity(
                reference_track, track, method, 
                ref_artist, ref_title, ref_filename, ref_duration
            )
            
            if similarity_score >= threshold:
                similar_tracks.append((track, idx, similarity_score))
        
        # Sort by similarity score (highest first)
        similar_tracks.sort(key=lambda x: x[2], reverse=True)
        
        return similar_tracks
    
    def _calculate_similarity(self, track1: pd.Series, track2: pd.Series, method: str,
                            ref_artist: str, ref_title: str, ref_filename: str, ref_duration: float) -> float:
        """Calculate similarity score between two tracks based on the specified method."""
        
        # Normalize track2 data
        artist2 = self._normalize_text(track2['artist'])
        title2 = self._normalize_text(track2['title'])
        filename2 = self._normalize_filename(track2.get('location', ''))
        duration2 = track2.get('totaltime', 0)
        
        if method == "artist_title":
            # Combined artist and title similarity
            artist_sim = fuzz.ratio(ref_artist, artist2)
            title_sim = fuzz.ratio(ref_title, title2)
            combined_sim = fuzz.ratio(f"{ref_artist} {ref_title}", f"{artist2} {title2}")
            
            # Weighted average (title more important)
            return (title_sim * 0.5) + (artist_sim * 0.3) + (combined_sim * 0.2)
            
        elif method == "title_only":
            # Title similarity only
            return fuzz.ratio(ref_title, title2)
            
        elif method == "filename":
            # Filename similarity
            return fuzz.ratio(ref_filename, filename2)
            
        elif method == "duration":
            # Duration + title similarity
            title_sim = fuzz.ratio(ref_title, title2)
            
            # Duration similarity (within 5 seconds = high similarity)
            if ref_duration > 0 and duration2 > 0:
                duration_diff = abs(ref_duration - duration2) / 1000  # Convert to seconds
                duration_sim = max(0, 100 - (duration_diff * 5))  # 5% penalty per second difference
                duration_sim = min(100, duration_sim)
            else:
                duration_sim = 0
            
            # Combined score
            return (title_sim * 0.7) + (duration_sim * 0.3)
        
        return 0
    
    def _create_duplicate_record(self, track: pd.Series, track_idx: int, group_id: int, 
                               rank: int, similarity: float, status: str) -> Dict:
        """Create a duplicate record for the results DataFrame."""
        return {
            'group_id': group_id,
            'rank': rank,
            'status': status,
            'similarity': similarity,
            'artist': track['artist'],
            'title': track['title'],
            'album': track['album'],
            'genre': track.get('genre', ''),
            'bpm': track.get('bpm', 0),
            'duration': track.get('totaltime', 0),
            'bitrate': track.get('bitrate', 0),
            'filetype': track.get('filetype', ''),
            'filesize': track.get('filesize', 0),
            'location': track.get('location', ''),
            'date_added': track.get('dateadded', ''),
            'play_count': track.get('playcount', 0),
            'track_index': track_idx
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better matching."""
        if not text or pd.isna(text):
            return ''
        
        # Convert to lowercase
        text = str(text).lower()
        
        # Remove common prefixes/suffixes
        text = re.sub(r'\b(the|a|an)\b', '', text)
        text = re.sub(r'\(.*?\)', '', text)  # Remove parentheses content
        text = re.sub(r'\[.*?\]', '', text)  # Remove bracket content
        text = re.sub(r'\s*-\s*(remix|edit|mix|version|remaster|remastered)\b.*', '', text)
        
        # Remove special characters and extra spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _normalize_filename(self, filepath: str) -> str:
        """Normalize filename for comparison."""
        if not filepath or pd.isna(filepath):
            return ''
        
        # Extract filename from path
        filename = filepath.split('/')[-1].split('\\')[-1]
        
        # Remove extension
        filename = re.sub(r'\.[^.]*$', '', filename)
        
        # Normalize like text
        return self._normalize_text(filename)
    
    def _load_digital_collection(self) -> pd.DataFrame:
        """Load digital collection from NML file."""
        try:
            parser = NMLParser(self.nml_path)
            df = parser.parse()
            logger.info(f"Loaded {len(df)} digital tracks from NML")
            return df
        except Exception as e:
            logger.error(f"Error loading digital collection: {e}")
            return pd.DataFrame()
    
    def get_duplicate_stats(self, duplicates_df: pd.DataFrame) -> Dict:
        """Generate statistics about found duplicates."""
        if duplicates_df.empty:
            return {}
        
        total_groups = duplicates_df['group_id'].nunique()
        total_duplicates = len(duplicates_df)
        potential_space_saved = 0
        
        # Calculate potential space savings
        for group_id in duplicates_df['group_id'].unique():
            group_tracks = duplicates_df[duplicates_df['group_id'] == group_id]
            if len(group_tracks) > 1:
                # Assume we keep the largest file and remove others
                filesizes = group_tracks['filesize'].astype(float)
                potential_space_saved += filesizes.sum() - filesizes.max()
        
        # Top duplicate artists/albums
        duplicate_tracks = duplicates_df[duplicates_df['status'] == 'duplicate']
        
        stats = {
            'total_groups': total_groups,
            'total_duplicate_tracks': len(duplicate_tracks),
            'original_tracks': len(duplicates_df[duplicates_df['status'] == 'original']),
            'potential_space_saved_mb': potential_space_saved / (1024 * 1024),
            'average_similarity': duplicate_tracks['similarity'].mean() if not duplicate_tracks.empty else 0,
            'top_duplicate_artists': duplicate_tracks['artist'].value_counts().head().to_dict(),
            'top_duplicate_albums': duplicate_tracks['album'].value_counts().head().to_dict(),
            'duplicate_formats': duplicate_tracks['filetype'].value_counts().to_dict(),
            'largest_groups': duplicates_df.groupby('group_id').size().sort_values(ascending=False).head().to_dict()
        }
        
        return stats


def find_duplicates_cli(nml_path: str = "./data/collection.nml", 
                       threshold: int = 85, method: str = "artist_title"):
    """Command-line interface for duplicate finding."""
    print("🔍 Starting Duplicate Search...")
    print(f"   Similarity threshold: {threshold}%")
    print(f"   Method: {method}")
    
    try:
        finder = DuplicateFinder(nml_path)
        duplicates = finder.find_duplicates(threshold, method)
        
        if not duplicates.empty:
            print(f"\n📊 Duplicate Search Results:")
            
            # Show summary
            stats = finder.get_duplicate_stats(duplicates)
            print(f"   Duplicate groups: {stats['total_groups']}")
            print(f"   Duplicate tracks: {stats['total_duplicate_tracks']}")
            print(f"   Potential space saved: {stats['potential_space_saved_mb']:.1f} MB")
            print(f"   Average similarity: {stats['average_similarity']:.1f}%")
            
            # Show sample results
            print(f"\n🎵 Sample Duplicate Groups:")
            for group_id in duplicates['group_id'].unique()[:3]:
                group = duplicates[duplicates['group_id'] == group_id]
                print(f"\n   Group {group_id}:")
                for _, track in group.iterrows():
                    status_icon = "🟢" if track['status'] == 'original' else "🔄"
                    print(f"     {status_icon} {track['artist']} - {track['title']} ({track['similarity']:.1f}%)")
            
            return duplicates
        else:
            print("✅ No duplicates found")
            return None
            
    except Exception as e:
        print(f"❌ Error during duplicate search: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Quick test
    import sys
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 85
    method = sys.argv[2] if len(sys.argv) > 2 else "artist_title"
    find_duplicates_cli(threshold=threshold, method=method)
