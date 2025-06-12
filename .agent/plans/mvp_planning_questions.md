# MVP Planning Questions for MusicTool

## Project Vision Summary
A music management tool that unifies physical vinyl collection (Discogs) and digital collection (Traktor NML) with metadata editing capabilities and sync mechanisms.

## Key Questions to Answer for MVP

### Data Architecture & Flow
- [x] **Question 1**: What is the primary data flow priority?
  - ~~Should we start with read-only analysis of existing collections?~~
  - ✅ **DECISION**: Focus on minimal collection manager - sync mechanism between local copy and NML from day one

### User Workflow Priority  
- [x] **Question 2**: What's the most valuable workflow for your daily use?
  - ✅ **DECISION**: Priority order for MVP development:
    1. **Gap Analysis**: "Show me vinyl tracks that aren't in my digital collection"
    2. **Metadata Cleanup**: "Let me fix artist names, genres, etc. in bulk" 
    3. **Collection Sync**: "Import new files and update everything"

### Technical Scope
- [x] **Question 3**: What's the minimum viable data model?
  - ~~Do we need full Discogs API integration in MVP?~~
  - ~~Can we start with just NML + CSV parsing?~~
  - ✅ **DECISION**: API-Enhanced approach required for MVP
    - **Reason**: Discogs CSV contains releases, NML contains tracks - need API to get track listings
    - **Implication**: MVP must include Discogs API integration from day one

### Risk Mitigation
- [x] **Question 4**: What's your comfort level with NML file modifications?
  - ~~Should MVP be completely read-only for safety?~~
  - ✅ **DECISION**: Backup-first approach - always create timestamped backups before any NML modifications
  - **Note**: User is appropriately paranoid about Traktor collection corruption 🛟

## Discussion Notes
**June 11, 2025 - Session 1**
- **Q1 Decision**: Building minimal collection manager with sync capabilities from start
- **Q4 Decision**: Backup-first approach for NML modifications
- **Q3 Decision**: API-Enhanced data model - must use Discogs API to get track listings from releases
- **UI Decision**: Streamlit for tabular data + wow effect
- **Architecture Decision**: API-first design with rapid prototyping UI (notebooks or Streamlit)
- **Q2 Decision**: Workflow priority: Gap Analysis → Metadata Cleanup → Collection Sync
- **Status**: ✅ All planning questions answered - implementation plan created!
- User wants to be able to make changes safely, not just analyze existing data
- User is appropriately paranoid about corrupting Traktor collection
- **Research confirmed**: No official Traktor API, NML file manipulation is the standard approach

## Next Steps: MVP Architecture Plan

**Based on our decisions, the MVP needs:**

### Architecture Approach: API-First + Rapid Prototyping UI

**Backend/API Layer:**
1. **Data Layer**: 
   - NML parser (read-only for MVP)
   - Discogs CSV parser  
   - Discogs API client with rate limiting
   - Local database/cache for track listings

2. **Core Logic**:
   - Release → Track expansion via API
   - Track matching algorithm (fuzzy matching for artist/title)
   - Gap identification engine

3. **Safety Layer**:
   - Backup system for NML files
   - Version tracking

**Frontend Options for Rapid MVP:**
- ~~**Option A**: Jupyter Notebooks + pandas DataFrames (great for data exploration/analysis)~~
- ✅ **Decision: Streamlit** (quick web UI with minimal code + great tabular data support)
- **Option C**: Hybrid - Notebooks for development/testing, Streamlit for user-facing MVP

**Streamlit Tabular Data Capabilities:**
- `st.dataframe()` - Interactive tables with sorting, filtering, search
- `st.data_editor()` - Editable tables (perfect for metadata cleanup!)
- `st.column_config` - Custom column types, formatting, validation
- Built-in pandas integration - zero friction with DataFrames
- Export capabilities (CSV, Excel)
- Pagination for large datasets

---
*Created: June 11, 2025*
*Next Update: After initial question responses*
