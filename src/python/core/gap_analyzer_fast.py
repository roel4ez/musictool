"""
Fast Gap Analyzer

Performance-optimized version of the gap analyzer that uses indexing and 
early termination to dramatically speed up the comparison process.

Author: MusicTool MVP
Created: June 12, 2025
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re
from collections import defaultdict
import time

from .nml_parser import NMLParser
from .collection_expander import CollectionExpander, load_api_key_from_env

logger = logging.getLogger(__name__)


class FastGapAnalyzer:
    """Performance-optimized gap analyzer for music collections."""
    
    def __init__(self, nml_path: str, db_path: str = "./data/musictool.db"):
        """
        Initialize the Fast Gap Analyzer.
        
        Args:
            nml_path: Path to NML file (digital collection)
            db_path: Path to SQLite database (physical collection)
        """
        self.nml_path = nml_path
        self.db_path = db_path
        
        # Load collections
        self.digital_collection = self._load_digital_collection()
        self.physical_collection = self._load_physical_collection()
        
        # Create search indexes for faster lookups
        self.digital_index = self._create_search_index(self.digital_collection)
        
        logger.info(f"Fast Gap Analyzer initialized:")
        logger.info(f"  Digital tracks: {len(self.digital_collection)}")
        logger.info(f"  Physical tracks: {len(self.physical_collection)}")
        logger.info(f"  Digital index entries: {len(self.digital_index)}")
    
    def find_gaps(self, confidence_threshold: int = 80, batch_size: int = 100) -> pd.DataFrame:
        """
        Find gaps between physical and digital collections with performance optimizations.
        
        Args:
            confidence_threshold: Minimum confidence score for matches (0-100)
            batch_size: Process tracks in batches for progress tracking
            
        Returns:
            DataFrame with gap analysis results
        """
        logger.info(f"Starting fast gap analysis (confidence threshold: {confidence_threshold}%)")
        start_time = time.time()
        
        if self.physical_collection.empty:
            logger.warning("No physical collection data found")
            return pd.DataFrame()
        
        if self.digital_collection.empty:
            logger.warning("No digital collection data found")
            return pd.DataFrame()
        
        gap_results = []
        total_tracks = len(self.physical_collection)
        
        # Process in batches for progress tracking
        for i in range(0, total_tracks, batch_size):
            batch_end = min(i + batch_size, total_tracks)
            batch = self.physical_collection.iloc[i:batch_end]
            
            logger.info(f"Processing batch {i//batch_size + 1}: tracks {i+1}-{batch_end} of {total_tracks}")
            
            # Process each track in the batch
            for idx, physical_track in batch.iterrows():
                result = self._find_track_in_digital_fast(physical_track, confidence_threshold)
                gap_results.append(result)
        
        # Convert to DataFrame
        gap_df = pd.DataFrame(gap_results)
        
        # Performance metrics
        elapsed_time = time.time() - start_time
        tracks_per_second = total_tracks / elapsed_time if elapsed_time > 0 else 0
        
        # Add summary statistics
        total_tracks = len(gap_df)
        found_tracks = len(gap_df[gap_df['status'] == 'found'])
        missing_tracks = len(gap_df[gap_df['status'] == 'missing'])
        
        logger.info(f"🎯 Fast gap analysis complete:")
        logger.info(f"  Total physical tracks: {total_tracks}")
        logger.info(f"  Found in digital: {found_tracks} ({found_tracks/total_tracks*100:.1f}%)")
        logger.info(f"  Missing from digital: {missing_tracks} ({missing_tracks/total_tracks*100:.1f}%)")
        logger.info(f"  Processing time: {elapsed_time:.2f}s ({tracks_per_second:.1f} tracks/sec)")
        
        return gap_df
    
    def _create_search_index(self, digital_df: pd.DataFrame) -> Dict[str, List[int]]:
        """Create a search index for faster lookups."""
        index = defaultdict(list)
        
        for idx, track in digital_df.iterrows():
            # Normalize and create search keys
            artist = self._normalize_text(track['artist'])
            title = self._normalize_text(track['title'])
            
            # Index by first few characters for quick filtering
            if artist:
                artist_prefix = artist[:3] if len(artist) >= 3 else artist
                index[f"artist:{artist_prefix}"].append(idx)
            
            if title:
                title_prefix = title[:3] if len(title) >= 3 else title
                index[f"title:{title_prefix}"].append(idx)
            
            # Index by combined key
            if artist and title:
                combined_prefix = f"{artist} {title}"[:6]
                index[f"combined:{combined_prefix}"].append(idx)
        
        return dict(index)
    
    def _find_track_in_digital_fast(self, physical_track: pd.Series, confidence_threshold: int) -> Dict:
        """Find a physical track in the digital collection using fast lookup."""
        
        # Normalize track info for matching
        phys_artist = self._normalize_text(physical_track['artist'])
        phys_title = self._normalize_text(physical_track['title'])
        
        # Get candidate tracks from index
        candidates = set()
        
        # Look up by artist prefix
        if phys_artist:
            artist_prefix = phys_artist[:3] if len(phys_artist) >= 3 else phys_artist
            candidates.update(self.digital_index.get(f"artist:{artist_prefix}", []))
        
        # Look up by title prefix
        if phys_title:
            title_prefix = phys_title[:3] if len(phys_title) >= 3 else phys_title
            candidates.update(self.digital_index.get(f"title:{title_prefix}", []))
        
        # Look up by combined prefix
        if phys_artist and phys_title:
            combined_prefix = f"{phys_artist} {phys_title}"[:6]
            candidates.update(self.digital_index.get(f"combined:{combined_prefix}", []))
        
        # If no candidates found, fall back to a small random sample
        if not candidates:
            # Take a small sample for fuzzy matching as last resort
            sample_size = min(100, len(self.digital_collection))
            candidates = set(self.digital_collection.sample(n=sample_size).index)
        
        # Limit candidates to reasonable number for performance
        if len(candidates) > 200:
            candidates = set(list(candidates)[:200])
        
        logger.debug(f"Checking {len(candidates)} candidates for: {phys_artist} - {phys_title}")
        
        best_match = None
        best_confidence = 0
        best_match_data = None
        
        # Create search strings
        phys_artist_title = f"{phys_artist} {phys_title}"
        
        # Search through candidate tracks only
        for idx in candidates:
            digital_track = self.digital_collection.iloc[idx]
            
            dig_artist = self._normalize_text(digital_track['artist'])
            dig_title = self._normalize_text(digital_track['title'])
            dig_artist_title = f"{dig_artist} {dig_title}"
            
            # Calculate similarity scores
            artist_score = fuzz.ratio(phys_artist, dig_artist)
            title_score = fuzz.ratio(phys_title, dig_title)
            combined_score = fuzz.ratio(phys_artist_title, dig_artist_title)
            
            # Weighted score (title is more important than artist)
            weighted_score = (title_score * 0.6) + (artist_score * 0.3) + (combined_score * 0.1)
            
            if weighted_score > best_confidence:
                best_confidence = weighted_score
                best_match_data = digital_track
                best_match = {
                    'digital_artist': digital_track['artist'],
                    'digital_title': digital_track['title'],
                    'digital_album': digital_track['album'],
                    'digital_genre': digital_track['genre'],
                    'digital_bpm': digital_track['bpm'],
                    'artist_score': artist_score,
                    'title_score': title_score,
                    'combined_score': combined_score
                }
                
                # Early termination for near-perfect matches
                if weighted_score >= 95:
                    logger.debug(f"Near-perfect match found ({weighted_score:.1f}%), stopping search")
                    break
        
        # Determine match status
        if best_confidence >= confidence_threshold:
            status = 'found'
            status_reason = f"Matched with {best_confidence:.1f}% confidence"
        else:
            status = 'missing'
            if best_confidence > 50:
                status_reason = f"Possible match at {best_confidence:.1f}% confidence (below threshold)"
            else:
                status_reason = "No good matches found"
        
        # Build result record
        result = {
            # Physical track info
            'physical_artist': physical_track['artist'],
            'physical_title': physical_track['title'],
            'physical_album': physical_track['album'],
            'physical_label': physical_track['label'],
            'physical_format': physical_track['format_type'],
            'physical_year': physical_track['release_year'],
            'physical_catalog': physical_track['catalog_number'],
            
            # Match results
            'status': status,
            'confidence': best_confidence,
            'status_reason': status_reason,
            
            # Best match info (if any)
            'digital_artist': best_match['digital_artist'] if best_match else '',
            'digital_title': best_match['digital_title'] if best_match else '',
            'digital_album': best_match['digital_album'] if best_match else '',
            'digital_genre': best_match['digital_genre'] if best_match else '',
            'digital_bpm': best_match['digital_bpm'] if best_match else 0,
            
            # Detailed scores
            'artist_score': best_match['artist_score'] if best_match else 0,
            'title_score': best_match['title_score'] if best_match else 0,
            'combined_score': best_match['combined_score'] if best_match else 0
        }
        
        return result
    
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
        
        # Remove special characters and extra spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
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
    
    def _load_physical_collection(self) -> pd.DataFrame:
        """Load physical collection from database."""
        try:
            api_key = load_api_key_from_env()
            if not api_key:
                logger.error("No API key found for loading physical collection")
                return pd.DataFrame()
            
            expander = CollectionExpander(api_key, self.db_path)
            df = expander.load_physical_collection()
            logger.info(f"Loaded {len(df)} physical tracks from database")
            return df
        except Exception as e:
            logger.error(f"Error loading physical collection: {e}")
            return pd.DataFrame()
