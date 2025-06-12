"""
Test script for Gap Analyzer

Test the gap analysis between physical and digital collections.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.python.core.gap_analyzer import GapAnalyzer, analyze_gaps_cli


def test_gap_analyzer():
    """Test the Gap Analyzer with our sample collections."""
    
    print("🎯 Testing Gap Analyzer...")
    print("Comparing 23 physical tracks vs 3,003 digital tracks")
    
    nml_file = "./data/collection.nml"
    
    if not os.path.exists(nml_file):
        print(f"❌ NML file not found: {nml_file}")
        return
    
    try:
        # Run gap analysis
        gap_results = analyze_gaps_cli(nml_file, confidence=80)
        
        if gap_results is not None and not gap_results.empty:
            print(f"\n🔍 Detailed Analysis:")
            
            # Show all results with details
            found_tracks = gap_results[gap_results['status'] == 'found']
            missing_tracks = gap_results[gap_results['status'] == 'missing']
            
            if not found_tracks.empty:
                print(f"\n✅ FOUND TRACKS ({len(found_tracks)}):")
                for idx, track in found_tracks.iterrows():
                    print(f"   🎵 {track['physical_artist']} - {track['physical_title']}")
                    print(f"      → {track['digital_artist']} - {track['digital_title']} ({track['confidence']:.1f}%)")
                    print(f"      Album: {track['physical_album']} → {track['digital_album']}")
                    print()
            
            if not missing_tracks.empty:
                print(f"\n❌ MISSING TRACKS ({len(missing_tracks)}):")
                for idx, track in missing_tracks.iterrows():
                    print(f"   🎵 {track['physical_artist']} - {track['physical_title']}")
                    print(f"      Album: {track['physical_album']} ({track['physical_year']})")
                    print(f"      Label: {track['physical_label']} [{track['physical_format']}]")
                    if track['confidence'] > 50:
                        print(f"      Best match: {track['digital_artist']} - {track['digital_title']} ({track['confidence']:.1f}%)")
                    print()
            
            # Additional insights
            print(f"🎪 Additional Insights:")
            print(f"   Confidence range: {gap_results['confidence'].min():.1f}% - {gap_results['confidence'].max():.1f}%")
            print(f"   Average artist score: {gap_results['artist_score'].mean():.1f}%")
            print(f"   Average title score: {gap_results['title_score'].mean():.1f}%")
            
            return gap_results
            
        else:
            print("❌ No gap analysis results")
            return None
            
    except Exception as e:
        print(f"❌ Error testing Gap Analyzer: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_gap_analyzer()
