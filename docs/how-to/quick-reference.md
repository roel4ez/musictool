# Collection Expansion Quick Reference

## Essential Commands

### Run Full Expansion
```bash
python3 run_full_expansion.py
```
- Processes all releases in your Discogs CSV
- Idempotent (safe to restart if interrupted)
- Rate limited to 1 API request/second
- Logs progress to `logs/expansion_*.log`

### Monitor Progress
```bash
python3 monitor_expansion.py
```
- Shows real-time expansion progress
- Displays processing rate and ETA
- Lists recently expanded releases
- Press Ctrl+C to stop monitoring

### Check Current Status
```bash
python3 -c "
import sqlite3, pandas as pd
conn = sqlite3.connect('./data/musictool.db')
df = pd.read_sql('SELECT * FROM expanded_tracks', conn)
releases = df['discogs_release_id'].nunique() if len(df) > 0 else 0
print(f'✅ {releases} releases expanded')
print(f'🎵 {len(df)} total tracks')
conn.close()
"
```

## Prerequisites Checklist

- [ ] Discogs API key in `.env` file
- [ ] Discogs CSV export in `./data/` folder
- [ ] Python dependencies installed (`pip install -r requirements.txt`)

## Timeline Estimates

| Collection Size | Estimated Time |
|----------------|----------------|
| 100 releases   | ~2-3 minutes   |
| 300 releases   | ~5-6 minutes   |
| 600 releases   | ~10-12 minutes |
| 1000+ releases | ~15-20 minutes |

## Recovery

If expansion stops, simply restart:
```bash
python3 run_full_expansion.py
```
Already processed releases will be skipped automatically.

## Next Steps

After expansion completes:
```bash
# Launch the web interface
streamlit run src/python/ui/streamlit_app.py

# Navigate to "Gap Analysis" to find missing tracks
```
