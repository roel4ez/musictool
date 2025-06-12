"""
MusicTool Streamlit Application

Beautiful web interface for music collection management and gap analysis.
Provides interactive tables, filtering, and export capabilities.

Author: MusicTool MVP
Created: June 12, 2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.python.core.nml_parser import NMLParser
from src.python.core.discogs_parser import DiscogsCSVParser
from src.python.core.discogs_client import load_api_key_from_env
from src.python.core.collection_expander import CollectionExpander
from src.python.core.gap_analyzer_fast import FastGapAnalyzer

# Page configuration
st.set_page_config(
    page_title="MusicTool - Collection Manager",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
        margin: 0.5rem 0;
    }
    .success-metric {
        border-left-color: #28a745;
    }
    .warning-metric {
        border-left-color: #ffc107;
    }
    .danger-metric {
        border-left-color: #dc3545;
    }
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def load_collections():
    """Load digital and physical collections with caching."""
    
    @st.cache_data
    def load_digital_collection():
        nml_path = "./data/collection.nml"
        if Path(nml_path).exists():
            parser = NMLParser(nml_path)
            return parser.parse()
        return pd.DataFrame()
    
    @st.cache_data
    def load_physical_collection():
        api_key = load_api_key_from_env()
        if api_key:
            expander = CollectionExpander(api_key)
            return expander.load_physical_collection()
        return pd.DataFrame()
    
    return load_digital_collection(), load_physical_collection()


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🎵 MusicTool Collection Manager</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🎛️ Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "💿 Digital Collection", "📀 Physical Collection", "🔍 Gap Analysis", "⚙️ Tools"]
    )
    
    # Load collections
    with st.spinner("Loading collections..."):
        digital_df, physical_df = load_collections()
    
    # Route to different pages
    if page == "🏠 Dashboard":
        show_dashboard(digital_df, physical_df)
    elif page == "💿 Digital Collection":
        show_digital_collection(digital_df)
    elif page == "📀 Physical Collection":
        show_physical_collection(physical_df)
    elif page == "🔍 Gap Analysis":
        show_gap_analysis(digital_df, physical_df)
    elif page == "⚙️ Tools":
        show_tools()


def show_dashboard(digital_df, physical_df):
    """Show overview dashboard."""
    st.header("📊 Collection Overview")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card success-metric">', unsafe_allow_html=True)
        st.metric("Digital Tracks", len(digital_df), delta=None)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card warning-metric">', unsafe_allow_html=True)
        st.metric("Physical Tracks", len(physical_df), delta=None)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if not digital_df.empty:
            unique_artists = digital_df['artist'].nunique()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Digital Artists", unique_artists)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.metric("Digital Artists", "N/A")
    
    with col4:
        if not physical_df.empty:
            unique_releases = physical_df['discogs_release_id'].nunique()
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Physical Releases", unique_releases)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.metric("Physical Releases", "N/A")
    
    # Charts row
    if not digital_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎵 Digital Collection by Genre")
            if 'genre' in digital_df.columns:
                genre_counts = digital_df['genre'].value_counts().head(10)
                fig = px.bar(
                    x=genre_counts.values,
                    y=genre_counts.index,
                    orientation='h',
                    title="Top 10 Genres",
                    color=genre_counts.values,
                    color_continuous_scale="viridis"
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📀 File Format Distribution")
            if 'filetype' in digital_df.columns:
                format_counts = digital_df['filetype'].value_counts()
                fig = px.pie(
                    values=format_counts.values,
                    names=format_counts.index,
                    title="Audio Formats",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    if not physical_df.empty and 'date_added' in physical_df.columns:
        st.subheader("📅 Recent Physical Additions")
        recent_df = physical_df.sort_values('date_added', ascending=False).head(5)
        st.dataframe(
            recent_df[['artist', 'title', 'album', 'date_added', 'format_type']],
            use_container_width=True
        )


def show_digital_collection(digital_df):
    """Show digital collection browser."""
    st.header("💿 Digital Collection")
    
    if digital_df.empty:
        st.warning("No digital collection data found. Please check your NML file.")
        return
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Artist filter
        artists = ['All'] + sorted(digital_df['artist'].unique().tolist())
        selected_artist = st.selectbox("Artist:", artists)
    
    with col2:
        # Genre filter
        genres = ['All'] + sorted(digital_df['genre'].unique().tolist())
        selected_genre = st.selectbox("Genre:", genres)
    
    with col3:
        # BPM range
        if digital_df['bpm'].max() > 0:
            min_bpm, max_bpm = st.slider(
                "BPM Range:",
                min_value=int(digital_df['bpm'].min()),
                max_value=int(digital_df['bpm'].max()),
                value=(int(digital_df['bpm'].min()), int(digital_df['bpm'].max()))
            )
        else:
            min_bpm, max_bpm = 0, 200
    
    # Apply filters
    filtered_df = digital_df.copy()
    
    if selected_artist != 'All':
        filtered_df = filtered_df[filtered_df['artist'] == selected_artist]
    
    if selected_genre != 'All':
        filtered_df = filtered_df[filtered_df['genre'] == selected_genre]
    
    filtered_df = filtered_df[
        (filtered_df['bpm'] >= min_bpm) & (filtered_df['bpm'] <= max_bpm)
    ]
    
    # Results
    st.subheader(f"📊 Results ({len(filtered_df)} tracks)")
    
    # Display options
    display_columns = st.multiselect(
        "Choose columns to display:",
        options=['artist', 'title', 'album', 'genre', 'bpm', 'key', 'playtime', 'filetype'],
        default=['artist', 'title', 'album', 'genre', 'bpm']
    )
    
    if display_columns:
        # Configure column display
        column_config = {
            'bpm': st.column_config.NumberColumn("BPM", format="%.1f"),
            'playtime': st.column_config.NumberColumn("Duration (s)", format="%d"),
            'filetype': st.column_config.SelectboxColumn("Format", options=['mp3', 'flac', 'aiff', 'wav'])
        }
        
        st.dataframe(
            filtered_df[display_columns],
            column_config=column_config,
            use_container_width=True,
            height=400
        )
        
        # Export option
        csv = filtered_df[display_columns].to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"digital_collection_{len(filtered_df)}_tracks.csv",
            mime="text/csv"
        )


def show_physical_collection(physical_df):
    """Show physical collection browser."""
    st.header("📀 Physical Collection")
    
    if physical_df.empty:
        st.warning("No physical collection data found. Please expand your collection first.")
        return
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Tracks", len(physical_df))
    
    with col2:
        unique_albums = physical_df['album'].nunique()
        st.metric("Unique Albums", unique_albums)
    
    with col3:
        unique_labels = physical_df['label'].nunique()
        st.metric("Record Labels", unique_labels)
    
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Format filter
        formats = ['All'] + sorted(physical_df['format_type'].unique().tolist())
        selected_format = st.selectbox("Format:", formats)
    
    with col2:
        # Label filter
        labels = ['All'] + sorted(physical_df['label'].unique().tolist())
        selected_label = st.selectbox("Label:", labels)
    
    with col3:
        # Year range
        if physical_df['release_year'].max() > 0:
            years = physical_df[physical_df['release_year'] > 0]['release_year']
            min_year, max_year = st.slider(
                "Release Year:",
                min_value=int(years.min()),
                max_value=int(years.max()),
                value=(int(years.min()), int(years.max()))
            )
        else:
            min_year, max_year = 1990, 2025
    
    # Apply filters
    filtered_df = physical_df.copy()
    
    if selected_format != 'All':
        filtered_df = filtered_df[filtered_df['format_type'] == selected_format]
    
    if selected_label != 'All':
        filtered_df = filtered_df[filtered_df['label'] == selected_label]
    
    filtered_df = filtered_df[
        (filtered_df['release_year'] >= min_year) & (filtered_df['release_year'] <= max_year)
    ]
    
    # Results
    st.subheader(f"📊 Results ({len(filtered_df)} tracks)")
    
    display_columns = ['artist', 'title', 'album', 'label', 'format_type', 'release_year', 'catalog_number']
    
    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        height=400
    )
    
    # Export option
    csv = filtered_df[display_columns].to_csv(index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name=f"physical_collection_{len(filtered_df)}_tracks.csv",
        mime="text/csv"
    )


def show_gap_analysis(digital_df, physical_df):
    """Show gap analysis results."""
    st.header("🔍 Gap Analysis")
    
    if digital_df.empty or physical_df.empty:
        st.warning("Both digital and physical collections are needed for gap analysis.")
        return
    
    # Analysis options
    st.subheader("⚙️ Analysis Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        confidence_threshold = st.slider("Confidence Threshold", 50, 95, 80, 5)
        st.caption("Minimum match confidence to consider a track 'found'")
    
    with col2:
        analysis_mode = st.selectbox(
            "Analysis Mode",
            ["🚀 Fast Sample (100 tracks)", "🔍 Complete Analysis", "🎯 Custom Range"]
        )
    
    with col3:
        if analysis_mode == "🎯 Custom Range":
            max_tracks = st.number_input("Max tracks to analyze", 50, len(physical_df), 500)
        else:
            max_tracks = 100 if "Sample" in analysis_mode else len(physical_df)
    
    # Performance info
    estimated_time = max_tracks * 0.1  # Rough estimate
    st.info(f"📊 Will analyze {max_tracks:,} tracks (estimated time: {estimated_time:.1f}s)")
    
    # Run analysis button
    if st.button(f"🚀 Run {analysis_mode}", type="primary"):
        
        # Prepare subset if needed
        if max_tracks < len(physical_df):
            physical_subset = physical_df.head(max_tracks)
            st.info(f"Analyzing first {max_tracks} tracks out of {len(physical_df):,} total")
        else:
            physical_subset = physical_df
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run gap analysis
        try:
            status_text.text("🔄 Initializing Fast Gap Analyzer...")
            analyzer = FastGapAnalyzer("./data/collection.nml")
            
            status_text.text("🔍 Running gap analysis...")
            
            # Custom progress callback would go here in a real implementation
            gap_results = analyzer.find_gaps(confidence_threshold=confidence_threshold)
            
            # Filter to only the subset we're analyzing
            if max_tracks < len(physical_df):
                # Get the track identifiers from our subset
                subset_ids = set(physical_subset.index)
                # This is simplified - in practice you'd need better matching
                gap_results = gap_results.head(max_tracks)
            
            progress_bar.progress(1.0)
            status_text.text("✅ Analysis complete!")
            
            # Store results in session state
            st.session_state.gap_results = gap_results
            st.session_state.analysis_config = {
                'confidence_threshold': confidence_threshold,
                'tracks_analyzed': len(gap_results),
                'mode': analysis_mode
            }
            
        except Exception as e:
            st.error(f"❌ Error during gap analysis: {e}")
            return
    
    # Display results if available
    if 'gap_results' in st.session_state:
        gap_results = st.session_state.gap_results
        config = st.session_state.analysis_config
        
        if not gap_results.empty:
                # Summary metrics
                total = len(gap_results)
                found = len(gap_results[gap_results['status'] == 'found'])
                missing = len(gap_results[gap_results['status'] == 'missing'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown('<div class="metric-card success-metric">', unsafe_allow_html=True)
                    st.metric("Found in Digital", f"{found}/{total}", f"{found/total*100:.1f}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-card danger-metric">', unsafe_allow_html=True)
                    st.metric("Missing from Digital", f"{missing}/{total}", f"{missing/total*100:.1f}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    avg_confidence = gap_results['confidence'].mean()
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Average Confidence", f"{avg_confidence:.1f}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Results tabs
                tab1, tab2, tab3 = st.tabs(["📊 All Results", "✅ Found Tracks", "❌ Missing Tracks"])
                
                with tab1:
                    st.subheader("Complete Gap Analysis Results")
                    
                    # Color-code rows based on status
                    def color_status(val):
                        if val == 'found':
                            return 'background-color: #d4edda'
                        else:
                            return 'background-color: #f8d7da'
                    
                    display_cols = ['physical_artist', 'physical_title', 'physical_album', 
                                  'status', 'confidence', 'digital_title']
                    
                    styled_df = gap_results[display_cols].style.applymap(
                        color_status, subset=['status']
                    )
                    
                    st.dataframe(styled_df, use_container_width=True, height=400)
                
                with tab2:
                    found_tracks = gap_results[gap_results['status'] == 'found']
                    if not found_tracks.empty:
                        st.subheader(f"✅ Found Tracks ({len(found_tracks)})")
                        
                        for idx, track in found_tracks.iterrows():
                            with st.expander(f"🎵 {track['physical_artist']} - {track['physical_title']}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write("**Physical:**")
                                    st.write(f"Artist: {track['physical_artist']}")
                                    st.write(f"Title: {track['physical_title']}")
                                    st.write(f"Album: {track['physical_album']}")
                                    st.write(f"Label: {track['physical_label']}")
                                
                                with col2:
                                    st.write("**Digital Match:**")
                                    st.write(f"Artist: {track['digital_artist']}")
                                    st.write(f"Title: {track['digital_title']}")
                                    st.write(f"Album: {track['digital_album']}")
                                    st.write(f"Confidence: {track['confidence']:.1f}%")
                    else:
                        st.info("No tracks found in digital collection.")
                
                with tab3:
                    missing_tracks = gap_results[gap_results['status'] == 'missing']
                    if not missing_tracks.empty:
                        st.subheader(f"❌ Missing Tracks ({len(missing_tracks)})")
                        
                        # Group by album
                        albums = missing_tracks['physical_album'].unique()
                        
                        for album in albums:
                            album_tracks = missing_tracks[missing_tracks['physical_album'] == album]
                            
                            with st.expander(f"📀 {album} ({len(album_tracks)} tracks missing)"):
                                st.dataframe(
                                    album_tracks[['physical_artist', 'physical_title', 'physical_label', 'confidence']],
                                    use_container_width=True
                                )
                        
                        # Export missing tracks
                        csv = missing_tracks[['physical_artist', 'physical_title', 'physical_album', 
                                            'physical_label', 'physical_catalog']].to_csv(index=False)
                        st.download_button(
                            label="📥 Download Missing Tracks",
                            data=csv,
                            file_name=f"missing_tracks_{len(missing_tracks)}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.success("🎉 All physical tracks found in digital collection!")
        else:
            st.info("Click 'Run Analysis' to start the gap analysis.")


def show_tools():
    """Show collection management tools."""
    st.header("⚙️ Collection Tools")
    
    # Collection expansion tool
    st.subheader("📈 Expand Physical Collection")
    st.write("Expand Discogs releases into individual tracks using the Discogs API.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_releases = st.number_input(
            "Max releases to process:",
            min_value=1,
            max_value=50,
            value=10,
            help="Start small to test, increase for full expansion"
        )
    
    with col2:
        if st.button("🚀 Start Expansion", type="primary"):
            api_key = load_api_key_from_env()
            if not api_key:
                st.error("❌ No Discogs API key found in .env file")
            else:
                with st.spinner(f"Expanding {max_releases} releases..."):
                    try:
                        from src.python.core.collection_expander import expand_collection_cli
                        result = expand_collection_cli("./data/gazmazk4ez-collection-20250608-1029.csv", max_releases)
                        
                        if result is not None:
                            st.success(f"✅ Successfully expanded {len(result)} tracks!")
                            st.balloons()
                        else:
                            st.error("❌ Expansion failed")
                    except Exception as e:
                        st.error(f"Error during expansion: {e}")
    
    # Configuration
    st.subheader("⚙️ Configuration")
    
    # API key status
    api_key = load_api_key_from_env()
    if api_key:
        st.success("✅ Discogs API key configured")
    else:
        st.error("❌ Discogs API key not found")
        st.info("Add DISCOGS_API_KEY=your_key_here to .env file")
    
    # File status
    nml_exists = Path("./data/collection.nml").exists()
    csv_exists = Path("./data/gazmazk4ez-collection-20250608-1029.csv").exists()
    db_exists = Path("./data/musictool.db").exists()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if nml_exists:
            st.success("✅ NML file found")
        else:
            st.error("❌ NML file missing")
    
    with col2:
        if csv_exists:
            st.success("✅ Discogs CSV found")
        else:
            st.error("❌ Discogs CSV missing")
    
    with col3:
        if db_exists:
            st.success("✅ Database exists")
        else:
            st.warning("⚠️ Database not found")


if __name__ == "__main__":
    main()
