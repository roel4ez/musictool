"""
Test script for Discogs CSV Parser

Quick test to validate the Discogs parser works with real data.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.python.core.discogs_parser import DiscogsCSVParser


def test_discogs_parser():
    """Test the Discogs CSV parser with the sample collection file."""
    csv_file = "./data/gazmazk4ez-collection-20250608-1029.csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ Discogs CSV file not found: {csv_file}")
        return
    
    try:
        print("🎵 Testing Discogs CSV Parser...")
        parser = DiscogsCSVParser(csv_file)
        df = parser.parse()
        
        print(f"✅ Successfully parsed {len(df)} releases")
        print("\n📊 Sample data:")
        print(df[['artist_clean', 'title', 'label', 'format_type', 'release_year']].head())
        
        print(f"\n📈 Summary stats:")
        print(f"- Unique artists: {df['artist_clean'].nunique()}")
        print(f"- Unique labels: {df['label'].nunique()}")
        print(f"- Collection folders: {df['collection_folder'].value_counts().to_dict()}")
        print(f"- Format types: {df['format_type'].value_counts().to_dict()}")
        print(f"- Release years: {df['release_year'].value_counts().head().to_dict()}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error testing Discogs parser: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_discogs_parser()
