# Full Collection Expansion Guide

This guide explains how to run the full collection expansion to convert your Discogs physical collection CSV into a detailed track-by-track database.

## Overview

The Collection Expander takes your Discogs CSV export (which contains releases/albums) and expands each release into individual tracks by fetching detailed tracklists from the Discogs API. This creates a comprehensive database of your physical music collection at the track level.

## Prerequisites

### 1. Discogs API Key
You need a Discogs API key to fetch release details:

1. Go to [Discogs Developer Settings](https://www.discogs.com/settings/developers)
2. Create a new application or use existing one
3. Copy your Personal Access Token
4. Add it to your `.env` file:

```bash
DISCOGS_API_KEY=your_api_key_here
```

### 2. Discogs CSV Export
Export your collection from Discogs:

1. Go to [Your Collection](https://www.discogs.com/user/your_username/collection)
2. Click "Export" at the top right
3. Download the CSV file
4. Place it in the `./data/` folder

### 3. Python Environment
Ensure you have the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Full Expansion

### Quick Start

```bash
# Run the full expansion on all releases
python3 run_full_expansion.py
```

### What Happens

1. **Prerequisite Check**: Verifies API key and CSV file exist
2. **Database Initialization**: Creates/connects to SQLite database
3. **Progress Assessment**: Shows current expansion status
4. **Idempotent Processing**: Skips already expanded releases
5. **API Fetching**: Retrieves tracklists at 1 request/second (rate limited)
6. **Progress Tracking**: Logs every 10 releases processed
7. **Error Handling**: Continues on errors, maintains progress

### Expected Output

```
🎵 Starting full collection expansion
📝 Logging to: logs/expansion_20250612_115735.log
✅ All prerequisites met
📊 Current database status:
   → 5 releases already expanded
   → 23 total tracks in database
🚀 Starting full collection expansion...
📁 Source: ./data/gazmazk4ez-collection-20250608-1029.csv
🗄️ Database: ./data/musictool.db
⚙️ Skip existing: True (idempotent)
🔄 Rate limiting: Enabled (1 req/sec)

Processing release 1/593: 1767
  → Digital - Deadline / Fix Up
  ✅ 2 tracks added and saved to database

Processing release 2/593: 5142
  → Nasty Habits - Liquid Fingers (Goldie Remix) / Deep Beats
  ✅ 2 tracks added and saved to database

📊 Progress: 10/593 releases processed (10 successful, 0 errors)
...
```

## Monitoring Progress

### Real-Time Monitor

Run the progress monitor in a separate terminal:

```bash
python3 monitor_expansion.py
```

This shows:
- Current progress percentage
- Processing rate (releases per minute)
- Estimated completion time
- Recently processed releases

Example monitor output:
```
🎵 MusicTool Collection Expansion Monitor
==================================================
📊 Total releases to process: 598
⏰ Started monitoring at: 11:58:13

🚀 Progress:  44/598 (  7.4%) | Tracks:  128 | Rate: 40.0/min | ETA: 16:30:15

📀 Recently expanded:
   → 33333: Bad Company - Rush Hour / Blind
   → 13346: Bad Company - The Nine / Dogfight
   → 108312: Rawhill Cru - Mo' Fire / Nitrous (Remixes)
```

### Manual Progress Check

Check database directly:

```bash
python3 -c "
import sqlite3
import pandas as pd
conn = sqlite3.connect('./data/musictool.db')
tracks = pd.read_sql('SELECT * FROM expanded_tracks', conn)
releases = tracks['discogs_release_id'].nunique()
print(f'Progress: {releases} releases, {len(tracks)} tracks')
conn.close()
"
```

## Key Features

### ✅ Idempotent Operation
- **Crash Recovery**: If the process stops (network issue, interruption), simply restart it
- **Skip Existing**: Already processed releases are automatically skipped
- **Progress Persistence**: Each release is saved immediately to the database
- **No Data Loss**: Safe to stop and restart at any time

### ✅ Rate Limiting
- **API Respectful**: Limited to 1 request per second
- **No Throttling**: Prevents hitting Discogs API rate limits
- **Sustainable**: Can run for hours without issues

### ✅ Comprehensive Logging
- **File Logging**: Detailed logs saved to `./logs/expansion_TIMESTAMP.log`
- **Console Output**: Real-time progress in terminal
- **Error Tracking**: All errors logged but processing continues
- **Statistics**: Regular progress summaries

## Expected Timeline

For a typical collection:
- **Small (100 releases)**: ~2-3 minutes
- **Medium (300 releases)**: ~5-6 minutes  
- **Large (600 releases)**: ~10-12 minutes
- **Very Large (1000+ releases)**: ~15-20 minutes

*Times may vary based on network speed and API response times*

## Output Database

The expansion creates a SQLite database at `./data/musictool.db` with:

### Table: `expanded_tracks`
```sql
CREATE TABLE expanded_tracks (
    id INTEGER PRIMARY KEY,
    artist TEXT NOT NULL,
    title TEXT NOT NULL, 
    position TEXT,
    duration TEXT,
    album TEXT,
    album_artist TEXT,
    label TEXT,
    catalog_number TEXT,
    release_year INTEGER,
    format_type TEXT,
    format_description TEXT,
    collection_folder TEXT,
    date_added TEXT,
    media_condition TEXT,
    sleeve_condition TEXT,
    notes TEXT,
    discogs_release_id INTEGER,
    source TEXT,
    expanded_date TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Sample Data
```
| artist              | title           | album           | discogs_release_id |
|--------------------|-----------------|-----------------|--------------------|
| A Guy Called Gerald | Voodoo Ray      | Essence         | 23143              |
| A Guy Called Gerald | Energy          | Essence         | 23143              |
| Bad Company         | Rush Hour       | Single          | 33333              |
| Matrix + Danny Jay  | Telepathy       | Single          | 239590             |
```

## Troubleshooting

### Common Issues

#### Missing API Key
```
❌ DISCOGS_API_KEY not found in environment or .env file
```
**Solution**: Add your Discogs API key to `.env` file

#### Missing CSV File  
```
❌ Discogs CSV not found: ./data/your-collection.csv
```
**Solution**: Export and download your collection CSV from Discogs

#### Network/API Errors
```
❌ Error processing release 12345: HTTP 503 Service Unavailable
```
**Solution**: The process will continue and retry. Temporary API issues are normal.

#### Database Lock Error
```
❌ Database is locked
```
**Solution**: Ensure no other processes are accessing the database

### Recovery from Interruption

If the expansion stops for any reason:

1. **Check Current Progress**:
   ```bash
   python3 monitor_expansion.py
   ```

2. **Simply Restart**:
   ```bash
   python3 run_full_expansion.py
   ```

3. **It Will Resume**: The process automatically skips completed releases

### Performance Optimization

For faster processing (at your own risk):
- Modify rate limiting in `core/discogs_client.py`
- Not recommended - may hit API limits

## Integration with Other Tools

After expansion completes:

### Gap Analysis
```bash
python3 -m streamlit run src/python/ui/streamlit_app.py
```
Navigate to "Gap Analysis" to find missing tracks

### Export Data
Use the Streamlit UI "Tools" section to export:
- Physical collection CSV
- Gap analysis results  
- Collection statistics

## Files Created

The expansion process creates:
- `./data/musictool.db` - Main database
- `./data/cache/` - API response cache
- `./logs/expansion_*.log` - Detailed logs

## Next Steps

After expansion:
1. **Review Results**: Check the Streamlit dashboard
2. **Run Gap Analysis**: Find missing digital tracks
3. **Export Reports**: Generate collection summaries
4. **Explore Data**: Use the collection browsers

---

*For technical details, see the source code in `src/python/core/collection_expander.py`*
