"""
Test script for Collection Expander

Test expanding a small number of vinyl releases into individual tracks.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.python.core.collection_expander import CollectionExpander, expand_collection_cli, load_api_key_from_env


def test_collection_expander():
    """Test the Collection Expander with a small number of releases."""
    
    print("🚀 Testing Collection Expander...")
    print("⚠️  Testing with only 5 releases to respect rate limits")
    
    # Check API key
    api_key = load_api_key_from_env()
    if not api_key:
        print("❌ No Discogs API key found in .env file")
        return
    
    csv_file = "./data/gazmazk4ez-collection-20250608-1029.csv"
    if not os.path.exists(csv_file):
        print(f"❌ Discogs CSV file not found: {csv_file}")
        return
    
    try:
        # Test expansion with 5 releases
        expanded_df = expand_collection_cli(csv_file, max_releases=5)
        
        if expanded_df is not None and not expanded_df.empty:
            print(f"\n📊 Sample expanded tracks:")
            print(expanded_df[['artist', 'title', 'album', 'format_type', 'release_year']].head(10))
            
            print(f"\n🎵 Track breakdown by release:")
            track_counts = expanded_df.groupby(['album', 'discogs_release_id']).size()
            for (album, release_id), count in track_counts.items():
                print(f"   {album[:40]:40} ({release_id}): {count} tracks")
            
            # Test loading from database
            print(f"\n💾 Testing database persistence...")
            expander = CollectionExpander(api_key)
            loaded_df = expander.load_physical_collection()
            print(f"✅ Loaded {len(loaded_df)} tracks from database")
            
            # Get expansion stats
            stats = expander.get_expansion_stats()
            print(f"\n📈 Collection stats:")
            print(f"   Total tracks: {stats['total_tracks']}")
            print(f"   Total releases: {stats['total_releases']}")
            print(f"   Unique artists: {stats['unique_artists']}")
            print(f"   Format breakdown: {stats['format_breakdown']}")
            print(f"   Year range: {stats['year_range']['earliest']}-{stats['year_range']['latest']}")
            
            return expanded_df
            
        else:
            print("❌ No tracks were expanded")
            return None
            
    except Exception as e:
        print(f"❌ Error testing Collection Expander: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_collection_expander()
