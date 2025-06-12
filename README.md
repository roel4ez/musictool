# MusicTool 🎵

A music collection manager that bridges physical and digital collections. Identifies gaps between your vinyl releases (Discogs) and digital tracks (Traktor NML) using fuzzy matching and API integration.

## Features

- **Collection Analysis**: Parse Traktor NML files and Discogs CSV exports
- **Gap Detection**: Find which vinyl tracks are missing from your digital collection
- **API Integration**: Expand Discogs releases into individual tracks via API
- **Interactive UI**: Beautiful Streamlit web interface with filtering and charts
- **Data Export**: Export gap analysis results and collection data

## Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Add your Discogs API key to .env file
```

### 2. Test Individual Components
```bash
# Test NML parser (digital collection)
python test_nml_parser.py

# Test Discogs CSV parser (physical collection)
python test_discogs_parser.py

# Test Discogs API client (rate limited)
python test_discogs_api.py

# Test collection expander (5 releases)
python test_collection_expander.py

# Test gap analysis
python test_gap_analyzer.py
```

### 3. Expand Physical Collection
```bash
# Run full collection expansion (idempotent, resumable)
python3 run_full_expansion.py

# Monitor progress in separate terminal
python3 monitor_expansion.py
```

### 4. Launch Streamlit App
```bash
# Start the web interface
streamlit run src/python/ui/streamlit_app.py

# Open browser to http://localhost:8501
```

## Data Sources

- **Digital**: Traktor Pro NML collection files (`data/collection.nml`)
- **Physical**: Discogs collection CSV export (`data/*.csv`)
- **API**: Discogs API for release tracklist expansion

## Architecture

```
NML Parser → Digital Collection (3,003 tracks)
Discogs CSV + API → Physical Collection (expanded tracks) → Gap Analysis → Results
```

Built with Python, Streamlit, pandas, SQLite, and fuzzy matching.

## Documentation

- **[Collection Expansion Guide](docs/how-to/collection-expansion.md)** - Complete guide to expanding your Discogs collection
- **[Project Vision](docs/project-description.md)** - Original project goals and requirements
- **[Architecture Decisions](docs/adrs/)** - Technical decisions and rationale
