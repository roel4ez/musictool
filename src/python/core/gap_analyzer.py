"""
Gap Analyzer

Compares physical and digital collections to identify gaps - tracks that exist
in one collection but not the other. Uses fuzzy matching for artist/title comparison.

Author: MusicTool MVP
Created: June 12, 2025
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re

from .nml_parser import NMLParser
from .collection_expander import CollectionExpander, load_api_key_from_env

logger = logging.getLogger(__name__)


class GapAnalyzer:
    """Analyzes gaps between physical and digital music collections."""
    
    def __init__(self, nml_path: str, db_path: str = "./data/musictool.db"):
        """
        Initialize the Gap Analyzer.
        
        Args:
            nml_path: Path to NML file (digital collection)
            db_path: Path to SQLite database (physical collection)
        """
        self.nml_path = nml_path
        self.db_path = db_path
        
        # Load collections
        self.digital_collection = self._load_digital_collection()
        self.physical_collection = self._load_physical_collection()
        
        logger.info(f"Gap Analyzer initialized:")
        logger.info(f"  Digital tracks: {len(self.digital_collection)}")
        logger.info(f"  Physical tracks: {len(self.physical_collection)}")
    
    def find_gaps(self, confidence_threshold: int = 80) -> pd.DataFrame:
        """
        Find gaps between physical and digital collections.
        
        Args:
            confidence_threshold: Minimum confidence score for matches (0-100)
            
        Returns:
            DataFrame with gap analysis results
        """
        logger.info(f"Starting gap analysis (confidence threshold: {confidence_threshold}%)")
        
        if self.physical_collection.empty:
            logger.warning("No physical collection data found")
            return pd.DataFrame()
        
        if self.digital_collection.empty:
            logger.warning("No digital collection data found")
            return pd.DataFrame()
        
        gap_results = []
        
        # For each physical track, try to find it in digital collection
        for idx, physical_track in self.physical_collection.iterrows():
            result = self._find_track_in_digital(physical_track, confidence_threshold)
            gap_results.append(result)
        
        # Convert to DataFrame
        gap_df = pd.DataFrame(gap_results)
        
        # Add summary statistics
        total_tracks = len(gap_df)
        found_tracks = len(gap_df[gap_df['status'] == 'found'])
        missing_tracks = len(gap_df[gap_df['status'] == 'missing'])
        
        logger.info(f"🎯 Gap analysis complete:")
        logger.info(f"  Total physical tracks: {total_tracks}")
        logger.info(f"  Found in digital: {found_tracks} ({found_tracks/total_tracks*100:.1f}%)")
        logger.info(f"  Missing from digital: {missing_tracks} ({missing_tracks/total_tracks*100:.1f}%)")
        
        return gap_df
    
    def _find_track_in_digital(self, physical_track: pd.Series, confidence_threshold: int) -> Dict:
        """Find a physical track in the digital collection."""
        
        # Normalize track info for matching
        phys_artist = self._normalize_text(physical_track['artist'])
        phys_title = self._normalize_text(physical_track['title'])
        
        # Create search strings
        phys_artist_title = f"{phys_artist} {phys_title}"
        
        best_match = None
        best_confidence = 0
        best_match_data = None
        
        # Search through digital collection
        for idx, digital_track in self.digital_collection.iterrows():
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
    
    def get_summary_stats(self, gap_df: pd.DataFrame) -> Dict:
        """Get summary statistics from gap analysis results."""
        if gap_df.empty:
            return {}
        
        total = len(gap_df)
        found = len(gap_df[gap_df['status'] == 'found'])
        missing = len(gap_df[gap_df['status'] == 'missing'])
        
        # Top missing artists/labels
        missing_tracks = gap_df[gap_df['status'] == 'missing']
        
        stats = {
            'total_physical_tracks': total,
            'found_in_digital': found,
            'missing_from_digital': missing,
            'found_percentage': (found / total * 100) if total > 0 else 0,
            'missing_percentage': (missing / total * 100) if total > 0 else 0,
            'average_confidence': gap_df['confidence'].mean(),
            'top_missing_artists': missing_tracks['physical_artist'].value_counts().head().to_dict(),
            'top_missing_labels': missing_tracks['physical_label'].value_counts().head().to_dict(),
            'missing_by_format': missing_tracks['physical_format'].value_counts().to_dict(),
            'missing_by_decade': self._group_by_decade(missing_tracks['physical_year']).to_dict()
        }
        
        return stats
    
    def _group_by_decade(self, years: pd.Series) -> pd.Series:
        """Group years into decades."""
        decades = (years // 10) * 10
        return decades.value_counts().sort_index()


def analyze_gaps_cli(nml_path: str = "./data/collection.nml", confidence: int = 80):
    """Command-line interface for gap analysis."""
    print("🎯 Starting Gap Analysis...")
    print(f"   Confidence threshold: {confidence}%")
    
    try:
        analyzer = GapAnalyzer(nml_path)
        gap_results = analyzer.find_gaps(confidence)
        
        if not gap_results.empty:
            print(f"\n📊 Gap Analysis Results:")
            
            # Show summary
            stats = analyzer.get_summary_stats(gap_results)
            print(f"   Found: {stats['found_in_digital']}/{stats['total_physical_tracks']} ({stats['found_percentage']:.1f}%)")
            print(f"   Missing: {stats['missing_from_digital']}/{stats['total_physical_tracks']} ({stats['missing_percentage']:.1f}%)")
            print(f"   Average confidence: {stats['average_confidence']:.1f}%")
            
            # Show sample results
            print(f"\n🎵 Sample Results:")
            display_cols = ['physical_artist', 'physical_title', 'status', 'confidence', 'digital_title']
            print(gap_results[display_cols].head(10).to_string(index=False))
            
            # Show missing tracks
            missing = gap_results[gap_results['status'] == 'missing']
            if not missing.empty:
                print(f"\n❌ Missing Tracks ({len(missing)}):")
                missing_display = missing[['physical_artist', 'physical_title', 'physical_album']].head(10)
                print(missing_display.to_string(index=False))
            
            return gap_results
        else:
            print("❌ No gap analysis results generated")
            return None
            
    except Exception as e:
        print(f"❌ Error during gap analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Quick test
    import sys
    confidence = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    analyze_gaps_cli(confidence=confidence)
