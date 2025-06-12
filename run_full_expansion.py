#!/usr/bin/env python3
"""
Full Collection Expansion Script

Runs the collection expander on all Discogs releases with proper logging,
error handling, and progress tracking. Designed to be idempotent and
recoverable from interruptions.

Usage:
    python run_full_expansion.py

Author: MusicTool MVP
Created: June 12, 2025
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src" / "python"))

from core.collection_expander import CollectionExpander
from core.discogs_client import load_api_key_from_env


def setup_logging():
    """Set up detailed logging for the expansion process."""
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"expansion_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"🎵 Starting full collection expansion")
    logger.info(f"📝 Logging to: {log_file}")
    
    return logger


def check_prerequisites():
    """Check that all required files and configurations exist."""
    logger = logging.getLogger(__name__)
    
    # Check for Discogs CSV
    csv_path = "./data/gazmazk4ez-collection-20250608-1029.csv"
    if not Path(csv_path).exists():
        logger.error(f"❌ Discogs CSV not found: {csv_path}")
        return False
    
    # Check for API key
    api_key = load_api_key_from_env()
    if not api_key:
        logger.error("❌ DISCOGS_API_KEY not found in environment or .env file")
        return False
    
    logger.info("✅ All prerequisites met")
    return True


def get_current_status(expander):
    """Get current expansion status."""
    logger = logging.getLogger(__name__)
    
    try:
        # Check existing database
        existing_tracks = expander.load_physical_collection()
        if len(existing_tracks) > 0:
            unique_releases = existing_tracks['discogs_release_id'].nunique()
            total_tracks = len(existing_tracks)
            logger.info(f"📊 Current database status:")
            logger.info(f"   → {unique_releases} releases already expanded")
            logger.info(f"   → {total_tracks} total tracks in database")
            return unique_releases, total_tracks
        else:
            logger.info("📊 Starting with empty database")
            return 0, 0
    except Exception as e:
        logger.info(f"📊 Starting with fresh database (error reading existing: {e})")
        return 0, 0


def main():
    """Main expansion process."""
    logger = setup_logging()
    
    try:
        # Check prerequisites
        if not check_prerequisites():
            logger.error("❌ Prerequisites not met. Exiting.")
            return 1
        
        # Initialize expander
        api_key = load_api_key_from_env()
        expander = CollectionExpander(api_key)
        
        # Get current status
        existing_releases, existing_tracks = get_current_status(expander)
        
        # Configuration
        csv_path = "./data/gazmazk4ez-collection-20250608-1029.csv"
        
        logger.info("🚀 Starting full collection expansion...")
        logger.info(f"📁 Source: {csv_path}")
        logger.info(f"🗄️ Database: ./data/musictool.db")
        logger.info(f"⚙️ Skip existing: True (idempotent)")
        logger.info(f"🔄 Rate limiting: Enabled (1 req/sec)")
        
        # Run expansion
        start_time = datetime.now()
        expanded_df = expander.expand_collection(
            csv_path,
            max_releases=None,  # Process all releases
            skip_existing=True  # Skip already processed releases
        )
        end_time = datetime.now()
        
        # Final report
        duration = end_time - start_time
        final_releases = expanded_df['discogs_release_id'].nunique() if len(expanded_df) > 0 else 0
        final_tracks = len(expanded_df)
        
        new_releases = final_releases - existing_releases
        new_tracks = final_tracks - existing_tracks
        
        logger.info("🎉 Full expansion completed!")
        logger.info(f"⏱️ Duration: {duration}")
        logger.info(f"📊 Final totals:")
        logger.info(f"   → {final_releases} releases ({new_releases} new)")
        logger.info(f"   → {final_tracks} tracks ({new_tracks} new)")
        
        if new_releases > 0:
            avg_tracks_per_release = new_tracks / new_releases if new_releases > 0 else 0
            logger.info(f"   → Average {avg_tracks_per_release:.1f} tracks per release")
        
        logger.info("✅ Collection expansion successful!")
        return 0
        
    except KeyboardInterrupt:
        logger.info("⏹️ Expansion interrupted by user")
        logger.info("💡 Progress has been saved. You can resume by running this script again.")
        return 1
    except Exception as e:
        logger.error(f"❌ Expansion failed: {e}")
        logger.exception("Full error details:")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
