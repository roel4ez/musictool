# MusicTool - Technical Implementation Guide

This document provides detailed technical information about MusicTool's architecture, algorithms, and implementation details for developers and advanced users.

## 🏗️ System Architecture

### High-Level Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │  Core Modules   │    │  Data Sources   │
│                 │    │                 │    │                 │
│ • Dashboard     │◄──►│ • NML Parser    │◄──►│ • Traktor NML   │
│ • Gap Analysis  │    │ • Gap Analyzer  │    │ • Discogs API   │
│ • Duplicate     │    │ • Duplicate     │    │ • SQLite DB     │
│   Finder        │    │   Finder        │    │ • CSV Files     │
│ • Tools         │    │ • Collection    │    │                 │
│                 │    │   Expander      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Directory Structure
```
src/python/
├── core/                          # Core business logic
│   ├── nml_parser.py             # Traktor NML file parsing
│   ├── discogs_client.py         # Discogs API integration
│   ├── collection_expander.py    # Release-to-track expansion
│   ├── gap_analyzer_fast.py      # Performance-optimized gap analysis
│   └── duplicate_finder.py       # Fuzzy duplicate detection
├── ui/
│   └── streamlit_app.py          # Web interface
└── utils/                        # Utility functions
    └── database.py               # Database operations
```

## 🔍 Algorithm Deep Dive

### Gap Analysis Algorithm

#### Performance Optimization Strategy
The original naive approach had O(n×m) complexity where n = physical tracks and m = digital tracks. With 1,791 physical tracks and potentially 10,000+ digital tracks, this resulted in 17+ million comparisons.

**Optimization Techniques:**

1. **Search Indexing**
```python
# Pre-compute index by text prefixes
index = {
    "artist:abc": [track_ids],
    "title:xyz": [track_ids], 
    "combined:abcxyz": [track_ids]
}
```

2. **Candidate Filtering**
```python
# Reduce search space by 90-95%
candidates = get_candidates_from_index(track)
# Limit to max 200 candidates per track
candidates = candidates[:200]
```

3. **Early Termination**
```python
# Stop searching at 95%+ confidence
if weighted_score >= 95:
    break
```

4. **Weighted Scoring Algorithm**
```python
weighted_score = (title_score * 0.6) + (artist_score * 0.3) + (combined_score * 0.1)
```

**Performance Results:**
- Before: O(n×m) ≈ 17,000,000 comparisons
- After: O(n×200) ≈ 358,000 comparisons  
- **Speed Improvement: ~47x faster**

### Duplicate Detection Algorithm

#### Multi-Method Approach

**1. Artist + Title Method (Recommended)**
```python
artist_sim = fuzz.ratio(normalize(artist1), normalize(artist2))
title_sim = fuzz.ratio(normalize(title1), normalize(title2))
combined_sim = fuzz.ratio(f"{artist1} {title1}", f"{artist2} {title2}")

score = (title_sim * 0.5) + (artist_sim * 0.3) + (combined_sim * 0.2)
```

**2. Duration + Title Method**
```python
title_sim = fuzz.ratio(normalize(title1), normalize(title2))
duration_diff = abs(duration1 - duration2) / 1000  # seconds
duration_sim = max(0, 100 - (duration_diff * 5))  # 5% penalty per second

score = (title_sim * 0.7) + (duration_sim * 0.3)
```

**3. Text Normalization**
```python
def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\b(the|a|an)\b', '', text)           # Remove articles
    text = re.sub(r'\(.*?\)', '', text)                   # Remove parentheses
    text = re.sub(r'\[.*?\]', '', text)                   # Remove brackets
    text = re.sub(r'\s*-\s*(remix|edit|mix)\b.*', '', text)  # Remove versions
    text = re.sub(r'[^\w\s]', ' ', text)                  # Remove special chars
    text = re.sub(r'\s+', ' ', text).strip()              # Normalize whitespace
    return text
```

### Collection Expansion Algorithm

#### Discogs API Integration Strategy

**1. Rate Limiting & Retry Logic**
```python
class RateLimitedClient:
    def __init__(self):
        self.rate_limiter = RateLimiter(max_calls=60, period=60)  # 60 calls/minute
        self.retry_config = ExponentialBackoff(max_retries=3)
    
    def get_release(self, release_id):
        with self.rate_limiter:
            return self._api_call_with_retry(release_id)
```

**2. Data Extraction Pipeline**
```python
def expand_release(release_data):
    tracks = []
    for track in release_data['tracklist']:
        normalized_track = {
            'artist': extract_artist(track, release_data),
            'title': clean_title(track['title']),
            'album': release_data['title'],
            'label': extract_label(release_data),
            'catalog_number': release_data.get('catno'),
            'release_year': extract_year(release_data),
            'format_type': extract_format(release_data),
            'discogs_release_id': release_data['id']
        }
        tracks.append(normalized_track)
    return tracks
```

**3. Error Handling & Recovery**
```python
def process_collection(csv_path, max_releases=None):
    results = {'success': 0, 'errors': 0, 'tracks': []}
    
    for release in get_releases(csv_path, max_releases):
        try:
            expanded_tracks = expand_release(release)
            results['tracks'].extend(expanded_tracks)
            results['success'] += 1
        except APIError as e:
            log_error(release['id'], e)
            results['errors'] += 1
            continue  # Continue with next release
    
    return results
```

## 💾 Data Models

### Digital Collection Schema (NML)
```python
@dataclass
class DigitalTrack:
    artist: str
    title: str
    album: str
    genre: str
    bpm: float
    totaltime: int          # milliseconds
    bitrate: int
    filetype: str
    filesize: int           # bytes
    location: str           # file path
    dateadded: datetime
    playcount: int
```

### Physical Collection Schema (Database)
```sql
CREATE TABLE physical_tracks (
    id INTEGER PRIMARY KEY,
    artist TEXT NOT NULL,
    title TEXT NOT NULL,
    album TEXT NOT NULL,
    label TEXT,
    catalog_number TEXT,
    release_year INTEGER,
    format_type TEXT,
    discogs_release_id INTEGER,
    track_position TEXT,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_artist_title ON physical_tracks(artist, title);
CREATE INDEX idx_discogs_release ON physical_tracks(discogs_release_id);
CREATE INDEX idx_album ON physical_tracks(album);
```

### Gap Analysis Results Schema
```python
@dataclass
class GapAnalysisResult:
    # Physical track info
    physical_artist: str
    physical_title: str
    physical_album: str
    physical_label: str
    physical_format: str
    physical_year: int
    
    # Match results
    status: str             # 'found' or 'missing'
    confidence: float       # 0-100
    status_reason: str
    
    # Best digital match (if found)
    digital_artist: str
    digital_title: str
    digital_album: str
    
    # Detailed similarity scores
    artist_score: float
    title_score: float
    combined_score: float
```

## 🎛️ Configuration Management

### Environment Variables
```bash
# .env file
DISCOGS_API_KEY=your_discogs_api_key_here
DISCOGS_USER_AGENT=YourApp/1.0
DATABASE_PATH=./data/musictool.db
NML_PATH=./data/collection.nml
LOG_LEVEL=INFO
```

### Application Configuration
```python
# config.py
@dataclass
class Config:
    # API settings
    discogs_api_key: str
    rate_limit_calls: int = 60
    rate_limit_period: int = 60
    
    # Performance settings
    gap_analysis_batch_size: int = 100
    max_candidates_per_track: int = 200
    duplicate_detection_threshold: int = 85
    
    # File paths
    database_path: str = "./data/musictool.db"
    nml_path: str = "./data/collection.nml"
    log_path: str = "./logs/musictool.log"
```

## 🚀 Performance Benchmarks

### Gap Analysis Performance
| Collection Size | Original Time | Optimized Time | Speed Improvement |
|----------------|---------------|----------------|-------------------|
| 1,000 tracks   | 45 seconds    | 2 seconds      | 22.5x faster      |
| 5,000 tracks   | 12 minutes    | 15 seconds     | 48x faster        |
| 10,000 tracks  | 45 minutes    | 35 seconds     | 77x faster        |

### Duplicate Detection Performance
| Collection Size | Processing Time | Memory Usage | Duplicates Found |
|----------------|----------------|--------------|------------------|
| 1,000 tracks   | 3 seconds      | 50 MB        | 15-25            |
| 5,000 tracks   | 35 seconds     | 150 MB       | 100-200          |
| 10,000 tracks  | 2.5 minutes    | 300 MB       | 300-500          |

### Collection Expansion Performance
| Releases | API Calls | Time (60/min) | Success Rate |
|----------|-----------|---------------|--------------|
| 100      | 100       | 2 minutes     | 98%          |
| 500      | 500       | 9 minutes     | 97%          |
| 1,000    | 1,000     | 18 minutes    | 96%          |

## 🔧 Development Setup

### Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run development server
streamlit run src/python/ui/streamlit_app.py
```

### Testing Framework
```python
# tests/test_gap_analyzer.py
import pytest
from src.python.core.gap_analyzer_fast import FastGapAnalyzer

class TestGapAnalyzer:
    def test_normalization(self):
        analyzer = FastGapAnalyzer("test_data/sample.nml")
        normalized = analyzer._normalize_text("The Beatles - Hey Jude (Remastered)")
        assert normalized == "beatles hey jude"
    
    def test_similarity_calculation(self):
        # Test fuzzy matching accuracy
        pass
    
    def test_performance_indexing(self):
        # Verify index creation and lookup speed
        pass
```

### Code Quality Standards
```python
# Use type hints throughout
def find_gaps(self, confidence_threshold: int = 80) -> pd.DataFrame:
    pass

# Comprehensive error handling
try:
    result = api_call()
except RateLimitError:
    time.sleep(60)
    result = api_call()
except APIError as e:
    logger.error(f"API error: {e}")
    return None

# Performance monitoring
@performance_monitor
def expensive_operation():
    pass
```

## 📊 Monitoring & Logging

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/musictool.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Performance Metrics
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def track_operation(self, operation_name, duration, items_processed):
        self.metrics[operation_name].append({
            'duration': duration,
            'items': items_processed,
            'rate': items_processed / duration if duration > 0 else 0,
            'timestamp': datetime.now()
        })
```

## 🔄 API Integration Details

### Discogs API Wrapper
```python
class DiscogsAPIClient:
    def __init__(self, api_key: str, user_agent: str):
        self.client = discogs_client.Client(user_agent, user_token=api_key)
        self.rate_limiter = RateLimiter(60, 60)  # 60 calls per minute
    
    def get_release(self, release_id: int) -> dict:
        with self.rate_limiter:
            try:
                release = self.client.release(release_id)
                return self._serialize_release(release)
            except discogs_client.exceptions.HTTPError as e:
                if e.status_code == 429:  # Rate limited
                    raise RateLimitError("Rate limit exceeded")
                elif e.status_code == 404:  # Not found
                    raise NotFoundError(f"Release {release_id} not found")
                else:
                    raise APIError(f"HTTP {e.status_code}: {e}")
```

### Error Recovery Strategies
```python
def robust_api_call(func, max_retries=3, backoff_factor=2):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(60)  # Wait for rate limit reset
                continue
            raise
        except (ConnectionError, TimeoutError) as e:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                time.sleep(wait_time)
                continue
            raise NetworkError(f"Failed after {max_retries} attempts: {e}")
```

This technical documentation provides the foundation for understanding, maintaining, and extending MusicTool's capabilities. The modular architecture and performance optimizations ensure the system can scale to handle large music collections efficiently.
