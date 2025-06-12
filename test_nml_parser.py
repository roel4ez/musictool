"""
Test script for NML Parser

Quick test to validate the NML parser works with real data.
Run this after installing requirements.txt
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.python.core.nml_parser import NMLParser


def test_nml_parser():
    """Test the NML parser with the sample collection file."""
    nml_file = "./data/collection.nml"
    
    if not os.path.exists(nml_file):
        print(f"❌ NML file not found: {nml_file}")
        return
    
    try:
        print("🎵 Testing NML Parser...")
        parser = NMLParser(nml_file)
        df = parser.parse()
        
        print(f"✅ Successfully parsed {len(df)} tracks")
        print("\n📊 Sample data:")
        print(df[['artist', 'title', 'filetype', 'filesize', 'bpm']].head())
        
        print(f"\n📈 Summary stats:")
        print(f"- Unique artists: {df['artist'].nunique()}")
        print(f"- Unique albums: {df['album'].nunique()}")
        print(f"- Genres: {df['genre'].nunique()}")
        print(f"- Average BPM: {df['bpm'].mean():.1f}")
        print(f"- File types: {df['filetype'].value_counts().to_dict()}")
        print(f"- Total collection size: {df['filesize'].sum() / (1024**3):.2f} GB")
        
        return df
        
    except Exception as e:
        print(f"❌ Error testing NML parser: {e}")
        return None


if __name__ == "__main__":
    test_nml_parser()
