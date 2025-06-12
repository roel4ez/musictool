"""
NML Parser for Traktor Collection Files

Parses Traktor NML (Native Instruments Markup Language) files and extracts
track information into a structured pandas DataFrame.

Author: MusicTool MVP
Created: June 12, 2025
"""

import pandas as pd
from lxml import etree
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class NMLParser:
    """Parser for Traktor NML collection files."""
    
    def __init__(self, nml_file_path: str):
        """
        Initialize the NML parser.
        
        Args:
            nml_file_path: Path to the NML file
        """
        self.nml_file_path = Path(nml_file_path)
        if not self.nml_file_path.exists():
            raise FileNotFoundError(f"NML file not found: {nml_file_path}")
    
    def parse(self) -> pd.DataFrame:
        """
        Parse the NML file and return a DataFrame with track information.
        
        Returns:
            pandas.DataFrame with columns:
            - artist: Artist name
            - title: Track title  
            - album: Album title
            - album_track: Track number on album
            - genre: Genre
            - label: Record label
            - bpm: Beats per minute
            - key: Musical key
            - playtime: Duration in seconds
            - file_path: Full file path
            - release_date: Release date
            - play_count: Number of times played
            - last_played: Last played date
            - filesize: File size in bytes
            - filetype: File extension (mp3, flac, aiff, etc.)
        """
        logger.info(f"Parsing NML file: {self.nml_file_path}")
        
        try:
            # Parse XML
            tree = etree.parse(str(self.nml_file_path))
            root = tree.getroot()
            
            # Extract all ENTRY elements
            entries = root.xpath("//ENTRY")
            logger.info(f"Found {len(entries)} tracks in NML file")
            
            tracks = []
            for entry in entries:
                track_data = self._extract_track_data(entry)
                if track_data:
                    tracks.append(track_data)
            
            # Convert to DataFrame
            df = pd.DataFrame(tracks)
            logger.info(f"Successfully parsed {len(df)} tracks")
            
            return df
            
        except Exception as e:
            logger.error(f"Error parsing NML file: {e}")
            raise
    
    def _extract_track_data(self, entry) -> Optional[Dict]:
        """Extract track data from a single ENTRY element."""
        try:
            # Basic track info from ENTRY attributes
            artist = entry.get('ARTIST', '').strip()
            title = entry.get('TITLE', '').strip()
            
            # Skip if missing essential data
            if not artist or not title:
                return None
            
            # Album information
            album_elem = entry.find('ALBUM')
            album = album_elem.get('TITLE', '') if album_elem is not None else ''
            album_track = album_elem.get('TRACK', '') if album_elem is not None else ''
            
            # File location
            location_elem = entry.find('LOCATION')
            file_path = ''
            if location_elem is not None:
                directory = location_elem.get('DIR', '').replace('/:', '/')
                filename = location_elem.get('FILE', '')
                file_path = f"{directory}{filename}" if directory and filename else ''
            
            # Track info
            info_elem = entry.find('INFO')
            genre = ''
            label = ''
            playtime = 0
            release_date = ''
            play_count = 0
            last_played = ''
            filesize = 0
            
            if info_elem is not None:
                genre = info_elem.get('GENRE', '')
                label = info_elem.get('LABEL', '')
                playtime = int(info_elem.get('PLAYTIME', '0'))
                release_date = info_elem.get('RELEASE_DATE', '')
                play_count = int(info_elem.get('PLAYCOUNT', '0'))
                last_played = info_elem.get('LAST_PLAYED', '')
                filesize = int(info_elem.get('FILESIZE', '0'))  # Filesize in bytes
            
            # Tempo/BPM
            tempo_elem = entry.find('TEMPO')
            bpm = 0.0
            if tempo_elem is not None:
                bpm = float(tempo_elem.get('BPM', '0'))
            
            # Musical key
            key_elem = entry.find('MUSICAL_KEY')
            key = ''
            if key_elem is not None:
                # Convert Traktor key value to readable format
                key_value = key_elem.get('VALUE', '')
                key = self._convert_key_value(key_value)
            
            # Extract filetype from file path
            filetype = ''
            if file_path:
                filetype = self._extract_filetype(file_path)
            
            return {
                'artist': artist,
                'title': title,
                'album': album,
                'album_track': album_track,
                'genre': genre,
                'label': label,
                'bpm': bpm,
                'key': key,
                'playtime': playtime,
                'file_path': file_path,
                'release_date': release_date,
                'play_count': play_count,
                'last_played': last_played,
                'filesize': filesize,
                'filetype': filetype
            }
            
        except Exception as e:
            logger.warning(f"Error extracting track data: {e}")
            return None
    
    def _convert_key_value(self, key_value: str) -> str:
        """Convert Traktor key value to readable musical key."""
        # Traktor uses numeric key values - this is a simplified conversion
        # You might want to expand this based on your needs
        if not key_value:
            return ''
        
        try:
            key_num = int(key_value)
            # This is a basic mapping - Traktor's key system is more complex
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            if 0 <= key_num <= 11:
                return f"{keys[key_num]}maj"
            elif 12 <= key_num <= 23:
                return f"{keys[key_num - 12]}min"
            else:
                return f"Key{key_value}"
        except ValueError:
            return key_value
    
    def _extract_filetype(self, file_path: str) -> str:
        """Extract file extension from file path."""
        if not file_path:
            return ''
        
        # Get the file extension (everything after the last dot)
        if '.' in file_path:
            filetype = file_path.split('.')[-1].lower()
            return filetype
        
        return ''


if __name__ == "__main__":
    # Quick test if run directly
    import sys
    if len(sys.argv) > 1:
        parser = NMLParser(sys.argv[1])
        df = parser.parse()
        print(f"Parsed {len(df)} tracks")
        print(df.head())
