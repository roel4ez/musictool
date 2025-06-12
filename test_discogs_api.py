"""
Test script for Discogs API Client

Careful testing with rate limiting - only tests a few releases.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.python.core.discogs_client import DiscogsAPIClient, load_api_key_from_env
from src.python.core.discogs_parser import DiscogsCSVParser


def test_discogs_api():
    """Test the Discogs API client with a few sample releases."""
    
    # Load API key
    api_key = load_api_key_from_env()
    if not api_key:
        print("❌ No Discogs API key found in .env file")
        print("Please add DISCOGS_API_KEY=your_key_here to .env")
        return
    
    print("🎵 Testing Discogs API Client...")
    print("⚠️  Testing with only 3 releases to respect rate limits")
    
    try:
        # Initialize client
        client = DiscogsAPIClient(api_key)
        
        # Get a few sample releases from the CSV
        csv_file = "./data/gazmazk4ez-collection-20250608-1029.csv"
        if os.path.exists(csv_file):
            parser = DiscogsCSVParser(csv_file)
            df = parser.parse()
            
            # Get first 3 release IDs for testing
            test_release_ids = df['release_id'].head(3).tolist()
            print(f"Testing with releases: {test_release_ids}")
            
            # Test batch fetch with limit
            results = client.batch_get_releases(test_release_ids, max_requests=3)
            
            print(f"\n✅ Successfully fetched {len(results)} releases")
            
            # Show sample data for each release
            for release_id, release_data in results.items():
                print(f"\n📀 Release {release_id}:")
                print(f"   Title: {release_data.get('title', 'Unknown')}")
                print(f"   Artists: {[a.get('name', '') for a in release_data.get('artists', [])]}")
                print(f"   Label: {[l.get('name', '') for l in release_data.get('labels', [])]}")
                print(f"   Year: {release_data.get('year', 'Unknown')}")
                
                # Get tracklist
                tracklist = client.get_release_tracklist(release_id)
                print(f"   Tracks: {len(tracklist)} found")
                
                # Show first few tracks
                for i, track in enumerate(tracklist[:3]):
                    if track['type_'] == 'track':  # Skip headings
                        print(f"      {track['position']}: {track['title']}")
                
                if len(tracklist) > 3:
                    print(f"      ... and {len(tracklist) - 3} more tracks")
            
            # Cache stats
            cache_stats = client.get_cache_stats()
            print(f"\n📊 Cache stats:")
            print(f"   Cached releases: {cache_stats['cached_releases']}")
            print(f"   Cache size: {cache_stats['cache_size_mb']:.2f} MB")
            
            return results
            
        else:
            print(f"❌ Discogs CSV file not found: {csv_file}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing Discogs API: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_discogs_api()
