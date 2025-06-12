"""
Discogs API Client

Handles communication with the Discogs API to fetch release details
and tracklists. Includes rate limiting and caching.

Author: MusicTool MVP
Created: June 12, 2025
"""

import requests
import time
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class DiscogsAPIClient:
    """Client for the Discogs API with rate limiting and caching."""
    
    def __init__(self, api_key: str, cache_dir: str = "./data/cache"):
        """
        Initialize the Discogs API client.
        
        Args:
            api_key: Discogs API key
            cache_dir: Directory for caching API responses
        """
        self.api_key = api_key
        self.base_url = "https://api.discogs.com"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting: Discogs allows 60 requests per minute
        self.requests_per_minute = 60
        self.min_delay = 60 / self.requests_per_minute  # 1 second between requests
        self.last_request_time = 0
        
        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Default headers
        self.session.headers.update({
            'User-Agent': 'MusicTool/1.0',
            'Authorization': f'Discogs token={api_key}'
        })
        
        logger.info(f"Discogs API client initialized with cache dir: {cache_dir}")
    
    def get_release(self, release_id: int, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a release.
        
        Args:
            release_id: Discogs release ID
            use_cache: Whether to use cached response if available
            
        Returns:
            Dictionary with release details or None if error
        """
        cache_file = self.cache_dir / f"release_{release_id}.json"
        
        # Check cache first
        if use_cache and cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    logger.debug(f"Using cached data for release {release_id}")
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading cache for release {release_id}: {e}")
        
        # Make API request
        try:
            url = f"{self.base_url}/releases/{release_id}"
            
            # Rate limiting
            self._wait_for_rate_limit()
            
            logger.info(f"Fetching release {release_id} from Discogs API")
            response = self.session.get(url)
            
            if response.status_code == 200:
                release_data = response.json()
                
                # Cache the response
                try:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(release_data, f, indent=2, ensure_ascii=False)
                    logger.debug(f"Cached release {release_id} data")
                except Exception as e:
                    logger.warning(f"Error caching release {release_id}: {e}")
                
                return release_data
                
            elif response.status_code == 404:
                logger.warning(f"Release {release_id} not found")
                return None
                
            elif response.status_code == 429:
                logger.warning(f"Rate limit hit for release {release_id}")
                time.sleep(60)  # Wait a minute and try again
                return self.get_release(release_id, use_cache=False)
                
            else:
                logger.error(f"API error for release {release_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching release {release_id}: {e}")
            return None
    
    def get_release_tracklist(self, release_id: int) -> List[Dict[str, Any]]:
        """
        Get the tracklist for a release.
        
        Args:
            release_id: Discogs release ID
            
        Returns:
            List of track dictionaries
        """
        release_data = self.get_release(release_id)
        if not release_data:
            return []
        
        tracks = []
        tracklist = release_data.get('tracklist', [])
        
        for track in tracklist:
            track_info = {
                'position': track.get('position', ''),
                'title': track.get('title', ''),
                'duration': track.get('duration', ''),
                'type_': track.get('type_', 'track'),  # track, heading, etc.
                'artists': self._extract_track_artists(track),
                'release_id': release_id
            }
            tracks.append(track_info)
        
        return tracks
    
    def batch_get_releases(self, release_ids: List[int], max_requests: int = 5) -> Dict[int, Dict[str, Any]]:
        """
        Get multiple releases with rate limiting.
        
        Args:
            release_ids: List of Discogs release IDs
            max_requests: Maximum number of API requests (for testing)
            
        Returns:
            Dictionary mapping release_id to release data
        """
        results = {}
        processed = 0
        
        logger.info(f"Fetching {min(len(release_ids), max_requests)} releases (limit: {max_requests})")
        
        for release_id in release_ids[:max_requests]:
            try:
                release_data = self.get_release(release_id)
                if release_data:
                    results[release_id] = release_data
                    processed += 1
                    logger.info(f"Progress: {processed}/{min(len(release_ids), max_requests)} releases fetched")
                else:
                    logger.warning(f"Failed to fetch release {release_id}")
                    
            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error processing release {release_id}: {e}")
                continue
        
        logger.info(f"Batch completed: {len(results)} releases fetched successfully")
        return results
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = self.min_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _extract_track_artists(self, track: Dict[str, Any]) -> List[str]:
        """Extract artist names from track data."""
        artists = []
        
        # Track-specific artists
        if 'artists' in track:
            for artist in track['artists']:
                if isinstance(artist, dict):
                    artists.append(artist.get('name', ''))
                else:
                    artists.append(str(artist))
        
        return artists
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about cached data."""
        cache_files = list(self.cache_dir.glob("release_*.json"))
        return {
            'cached_releases': len(cache_files),
            'cache_size_mb': sum(f.stat().st_size for f in cache_files) / (1024 * 1024)
        }


def load_api_key_from_env() -> Optional[str]:
    """Load Discogs API key from environment variables."""
    from dotenv import load_dotenv
    
    # Load .env file
    load_dotenv()
    
    api_key = os.getenv('DISCOGS_API_KEY')
    if not api_key:
        logger.error("DISCOGS_API_KEY not found in environment variables")
        return None
    
    return api_key


if __name__ == "__main__":
    # Quick test if run directly
    api_key = load_api_key_from_env()
    if api_key:
        client = DiscogsAPIClient(api_key)
        
        # Test with a single release
        test_release = client.get_release(23143)  # A Guy Called Gerald - Essence
        if test_release:
            print(f"Test successful: {test_release.get('title', 'Unknown')}")
            tracklist = client.get_release_tracklist(23143)
            print(f"Tracks found: {len(tracklist)}")
        else:
            print("Test failed")
    else:
        print("No API key found")
