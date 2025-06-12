"""
Discogs CSV Parser for Collection Exports

Parses Discogs collection CSV exports and extracts release information
into a structured pandas DataFrame.

Author: MusicTool MVP
Created: June 12, 2025
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DiscogsCSVParser:
    """Parser for Discogs collection CSV export files."""
    
    def __init__(self, csv_file_path: str):
        """
        Initialize the Discogs CSV parser.
        
        Args:
            csv_file_path: Path to the Discogs CSV export file
        """
        self.csv_file_path = Path(csv_file_path)
        if not self.csv_file_path.exists():
            raise FileNotFoundError(f"Discogs CSV file not found: {csv_file_path}")
    
    def parse(self) -> pd.DataFrame:
        """
        Parse the Discogs CSV file and return a DataFrame with release information.
        
        Returns:
            pandas.DataFrame with columns:
            - catalog_number: Catalog number
            - artist: Artist name
            - title: Release title
            - label: Record label
            - format: Format description (LP, 12", etc.)
            - rating: User rating
            - released: Release year
            - release_id: Discogs release ID
            - collection_folder: Collection folder name
            - date_added: Date added to collection
            - media_condition: Media condition
            - sleeve_condition: Sleeve condition
            - notes: Collection notes
        """
        logger.info(f"Parsing Discogs CSV file: {self.csv_file_path}")
        
        try:
            # Read CSV file
            df = pd.read_csv(str(self.csv_file_path))
            logger.info(f"Found {len(df)} releases in Discogs CSV")
            
            # Clean and standardize column names
            df = self._clean_dataframe(df)
            
            # Handle data cleaning and normalization
            df = self._normalize_data(df)
            
            logger.info(f"Successfully parsed {len(df)} releases")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing Discogs CSV file: {e}")
            raise
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the DataFrame columns."""
        
        # Map Discogs CSV columns to our standard naming
        column_mapping = {
            'Catalog#': 'catalog_number',
            'Artist': 'artist', 
            'Title': 'title',
            'Label': 'label',
            'Format': 'format',
            'Rating': 'rating',
            'Released': 'released',
            'release_id': 'release_id',
            'CollectionFolder': 'collection_folder',
            'Date Added': 'date_added',
            'Collection Media Condition': 'media_condition',
            'Collection Sleeve Condition': 'sleeve_condition',
            'Collection Notes': 'notes'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Fill NaN values with empty strings for text columns
        text_columns = ['catalog_number', 'artist', 'title', 'label', 'format', 
                       'collection_folder', 'media_condition', 'sleeve_condition', 'notes']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str)
        
        return df
    
    def _normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize and clean the data."""
        
        # Clean catalog numbers - handle multiple formats
        if 'catalog_number' in df.columns:
            df['catalog_number_clean'] = df['catalog_number'].apply(self._clean_catalog_number)
        
        # Parse release year
        if 'released' in df.columns:
            df['release_year'] = df['released'].apply(self._parse_release_year)
        
        # Clean artist names
        if 'artist' in df.columns:
            df['artist_clean'] = df['artist'].apply(self._clean_artist_name)
        
        # Extract format info
        if 'format' in df.columns:
            df['format_type'] = df['format'].apply(self._extract_format_type)
            df['format_description'] = df['format'].apply(self._extract_format_description)
        
        # Convert date_added to datetime
        if 'date_added' in df.columns:
            df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
        
        return df
    
    def _clean_catalog_number(self, catalog_num: str) -> str:
        """Clean and standardize catalog numbers."""
        if not catalog_num or catalog_num == 'nan':
            return ''
        
        # Remove extra quotes and whitespace
        catalog_clean = str(catalog_num).strip().strip('"')
        
        # Handle multiple catalog numbers (comma or space separated)
        if ',' in catalog_clean:
            # Take the first one for primary key
            catalog_clean = catalog_clean.split(',')[0].strip()
        
        return catalog_clean
    
    def _parse_release_year(self, released: str) -> int:
        """Extract release year from various date formats."""
        if not released or str(released) == 'nan':
            return 0
        
        try:
            # Convert to string and extract year
            year_str = str(released).strip()
            if year_str.isdigit() and len(year_str) == 4:
                return int(year_str)
            else:
                # Try to extract 4-digit year from string
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', year_str)
                if year_match:
                    return int(year_match.group())
        except (ValueError, AttributeError):
            pass
        
        return 0
    
    def _clean_artist_name(self, artist: str) -> str:
        """Clean and normalize artist names."""
        if not artist or artist == 'nan':
            return ''
        
        artist_clean = str(artist).strip()
        
        # Handle "Various" artists
        if artist_clean.lower() in ['various', 'various artists']:
            return 'Various'
        
        # Remove extra whitespace
        artist_clean = ' '.join(artist_clean.split())
        
        return artist_clean
    
    def _extract_format_type(self, format_str: str) -> str:
        """Extract the primary format type (LP, 12", CD, etc.)."""
        if not format_str or format_str == 'nan':
            return ''
        
        format_lower = str(format_str).lower()
        
        # Common format patterns
        if 'lp' in format_lower:
            return 'LP'
        elif '12"' in format_str or '12 inch' in format_lower:
            return '12"'
        elif '7"' in format_str or '7 inch' in format_lower:
            return '7"'
        elif 'cd' in format_lower:
            return 'CD'
        elif 'cassette' in format_lower or 'tape' in format_lower:
            return 'Cassette'
        else:
            return 'Other'
    
    def _extract_format_description(self, format_str: str) -> str:
        """Extract detailed format description."""
        if not format_str or format_str == 'nan':
            return ''
        
        # Clean up format string
        desc = str(format_str).strip().strip('"')
        return desc


if __name__ == "__main__":
    # Quick test if run directly
    import sys
    if len(sys.argv) > 1:
        parser = DiscogsCSVParser(sys.argv[1])
        df = parser.parse()
        print(f"Parsed {len(df)} releases")
        print(df.head())
