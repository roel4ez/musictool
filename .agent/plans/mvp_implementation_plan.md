# MusicTool MVP Implementation Plan

## Project Overview
**Goal**: Build a minimal collection manager with Gap Analysis using API-first design + Streamlit UI

**Architecture**: Backend API → Streamlit Frontend
**Primary Workflow**: Identify vinyl tracks missing from digital collection

---

## Phase 1: Foundation & Data Layer (Week 1-2)

### 1.1 Project Setup
- [x] Set up Python environment with dependencies
  - `streamlit`, `pandas`, `requests`, `python-dotenv`
  - `lxml` for NML parsing, `fuzzywuzzy` for matching
- [x] Create proper folder structure following guidelines
- [x] Set up environment configuration

### 1.2 Data Parsers (Core API Layer)
- [x] **NML Parser** (`src/python/core/nml_parser.py`)
  - Parse Traktor collection XML
  - Extract: Artist, Title, Album, Genre, File Path, BPM, Key, Filesize, Filetype
  - Return structured pandas DataFrame
  - ✅ **TESTED**: Successfully parsed 3,003 tracks from real collection
  - ✅ **ENHANCED**: Added filesize and filetype extraction
  - 🐛 **KNOWN ISSUE**: Filesize values seem too low (~60MB total) - needs investigation
  
- [x] **Discogs CSV Parser** (`src/python/core/discogs_parser.py`)
  - Parse Discogs collection export
  - Extract: Artist, Release Title, Catalog Number, Label, Format, Year
  - Handle inconsistencies in catalog numbers/formats
  - ✅ **TESTED**: Successfully parsed 598 releases from real collection
  - ✅ **INSIGHTS**: 98% DnB collection, 345 artists, 229 labels, primarily 12" format

- [x] **Discogs API Client** (`src/python/core/discogs_client.py`)
  - Rate-limited API calls (60 requests/minute)
  - Fetch release details by ID
  - Cache responses locally (JSON files)
  - Error handling and retry logic
  - ✅ **TESTED**: Successfully fetched 3 releases with full tracklist data
  - ✅ **FEATURES**: Rate limiting, caching, batch processing, tracklist extraction

- [x] **Collection Expander** (`src/python/core/collection_expander.py`)
  - **Core Function**: Transform Discogs releases → individual tracks
  - For each release in CSV: API call → get tracklist → create track records
  - Merge release metadata (label, year, format) with track data
  - Handle multi-disc releases, bonus tracks, variations
  - Progress tracking for bulk expansion operations
  - ✅ **TESTED**: Successfully expanded 5 releases → 23 tracks
  - ✅ **FEATURES**: SQLite persistence, rate limiting, comprehensive metadata

- [ ] **Collection Storage** (`src/python/core/collection_storage.py`)
  - Persist expanded physical collection (SQLite or Parquet)
  - Track expansion timestamps and source CSV checksums
  - Smart incremental updates (only expand new/changed releases)
  - Export/import functionality for backup/sharing

### 1.3 Data Models
- [ ] Define unified track/release data structures
- [ ] Create data validation and cleaning utilities

---

## Phase 2: Gap Analysis Engine (Week 2-3)

### 2.1 Track Matching Algorithm
- [x] **Fuzzy Matching Logic** (`src/python/core/gap_analyzer.py`)
  - Artist name normalization (case, punctuation, "The", etc.)
  - Title matching with confidence scores
  - Album/release correlation
  - Handle various edge cases
  - ✅ **TESTED**: 23 physical vs 3,003 digital tracks analyzed successfully

### 2.2 Gap Analysis Core
- [x] **Gap Finder** (`src/python/core/gap_analyzer.py`)
  - Load NML tracks (digital collection)
  - Load persisted physical collection (expanded vinyl tracks)
  - Execute matching algorithm between the two datasets
  - Generate gap analysis report with confidence scores
  - ✅ **RESULTS**: Found 5/23 matches (21.7%), identified 18 gaps (78.3%)
  - ✅ **INSIGHTS**: Entire "Essence" LP missing, perfect matches on exact titles

### 2.3 Caching & Performance
- [ ] Local cache for Discogs API responses
- [ ] Persisted physical collection database (avoid re-expansion)
- [ ] Incremental updates (only process new releases)
- [ ] Progress tracking for long-running operations

---

## Phase 3: Streamlit UI (Week 3-4) ✅ COMPLETE

### 3.1 Main Application Structure
- [x] **App Layout** (`src/python/ui/streamlit_app.py`)
  - Sidebar navigation with emoji icons
  - Data loading with caching
  - Multi-page application structure
  - Custom CSS styling with gradients
  - ✅ **DEPLOYED**: Live at http://localhost:8501

### 3.2 Core UI Components
- [x] **Dashboard Page**
  - Collection overview metrics
  - Interactive Plotly charts (genres, formats)
  - Recent activity tracking
  - Beautiful gradient header

- [x] **Gap Analysis Dashboard**
  - Live gap analysis with confidence scoring
  - Color-coded results (green=found, red=missing)
  - Expandable track details
  - Export functionality for missing tracks
  - Tabbed interface for organized viewing

- [x] **Collection Browsers**
  - Digital collection: 3,003 tracks with filtering
  - Physical collection: Expanded vinyl tracks
  - Multi-column filters (artist, genre, BPM, format, year)
  - Customizable column display
  - CSV export capabilities

### 3.3 User Experience Features
- [x] Beautiful styling with custom CSS
- [x] Color-coded metric cards
- [x] Progress spinners for long operations
- [x] Error handling with user-friendly messages
- [x] File status validation in Tools page
- [x] API key configuration checking
- ✅ **WOW FACTOR ACHIEVED**: Professional UI with excellent UX

### 3.1 Main Application Structure
- [ ] **App Layout** (`src/python/ui/streamlit_app.py`)
  - Sidebar navigation
  - Data loading section
  - Results display area
  - Configuration panels

### 3.2 Core UI Components
- [ ] **File Upload/Path Selection**
  - NML file picker
  - Discogs CSV upload
  - API key configuration

- [ ] **Gap Analysis Dashboard**
  - Interactive results table with filtering
  - Summary statistics (X missing out of Y total)
  - Export functionality
  - Color-coded status indicators

- [ ] **Collection Browser**
  - View NML collection (digital tracks)
  - View persisted physical collection (expanded vinyl tracks)
  - Compare collections side-by-side
  - Search and filter capabilities

### 3.3 User Experience Features
- [ ] Progress bars for API operations
- [ ] Error handling with user-friendly messages
- [ ] Configuration persistence
- [ ] Basic help/documentation

---

## Phase 4: Safety & Polish (Week 4-5)

### 4.1 Backup System
- [ ] **NML Backup Manager** (`src/python/core/backup_manager.py`)
  - Timestamped backups before any modifications
  - Backup verification
  - Restore functionality

### 4.2 Configuration & Deployment
- [ ] Environment configuration management
- [ ] Docker containerization (optional)
- [ ] Local deployment instructions
- [ ] Error logging and monitoring

### 4.3 Testing & Validation
- [ ] Unit tests for core matching logic
- [ ] Integration tests with sample data
- [ ] User acceptance testing with real collection

---

## Success Criteria for MVP

**✅ MVP Complete When:**
1. Can load NML and Discogs CSV files
2. Expands Discogs releases to track listings via API
3. Identifies gaps with confidence scores
4. Displays results in interactive Streamlit table
5. Allows export of gap analysis results
6. Has basic error handling and user feedback

**📊 Example MVP Output:**
```
Gap Analysis Results (showing 127 missing tracks out of 1,453 vinyl tracks)

| Artist          | Album                | Track              | Confidence | Status  |
|-----------------|----------------------|--------------------|------------|---------|
| Daft Punk       | Discovery            | One More Time      | 95%        | Missing |
| Justice         | Cross                | Genesis            | 89%        | Missing |
| Moderat         | II                   | Bad Kingdom        | 92%        | Missing |
```

---

## Future Phases (Post-MVP)
- **Phase 5**: Metadata Cleanup UI with batch editing
- **Phase 6**: Collection Sync (NML write-back with backups)
- **Phase 7**: Advanced features (duplicate detection, format analysis)

---

**Ready to start Phase 1? Let's build this! 🎵**

*Created: June 11, 2025*
*Last Update: June 12, 2025 - Completed Phase 1.1 (Project Setup)*
