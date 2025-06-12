# MusicTool - User Guide

Welcome to MusicTool! This comprehensive guide will help you get started with analyzing and managing your music collection using our powerful suite of tools.

## 🚀 Quick Start Guide

### Prerequisites
Before you begin, make sure you have:
- ✅ Python 3.8 or higher installed
- ✅ A Discogs account with API access
- ✅ Your Traktor collection exported as `.nml` file
- ✅ Your Discogs collection exported as CSV

### Step 1: Initial Setup

#### 1.1 Get Your Discogs API Key
1. Go to [Discogs Developer Settings](https://www.discogs.com/settings/developers)
2. Click "Generate new token"
3. Copy your personal access token
4. Save it securely - you'll need it for setup

#### 1.2 Export Your Collections

**Traktor Digital Collection:**
1. Open Native Instruments Traktor
2. Go to File → Export Collection
3. Save as `collection.nml` in the `data/` folder

**Discogs Physical Collection:**
1. Log into your Discogs account
2. Go to Your Collection
3. Click "Export" and download CSV
4. Save the CSV file in the `data/` folder

#### 1.3 Configure MusicTool
1. Create a `.env` file in the project root
2. Add your Discogs API key:
```
DISCOGS_API_KEY=your_api_key_here
```

### Step 2: Launch MusicTool
```bash
# Navigate to the project directory
cd musictool

# Install dependencies (first time only)
pip install -r requirements.txt

# Launch the application
streamlit run src/python/ui/streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

---

## 📱 User Interface Guide

### Navigation
The sidebar on the left contains the main navigation menu:
- **🏠 Dashboard**: Overview of your collections
- **💿 Digital Collection**: Browse your digital tracks
- **📀 Physical Collection**: Explore your physical releases
- **🔍 Gap Analysis**: Find missing digital tracks
- **🔄 Duplicate Finder**: Detect duplicate files
- **⚙️ Tools**: Collection management utilities

---

## 🏠 Dashboard Overview

The Dashboard provides a bird's-eye view of your entire music collection.

### What You'll See:
- **Collection Metrics**: Total tracks, artists, and releases
- **Visual Charts**: Genre distribution and file format breakdown
- **Recent Activity**: Latest additions to your collection
- **Quick Stats**: Key performance indicators

### Pro Tips:
- Use the Dashboard to spot trends in your collection
- Check file format distribution to ensure quality consistency
- Monitor collection growth over time

---

## 💿 Digital Collection Management

### Features:
- **Complete Track Listing**: Every track in your digital library
- **Advanced Filtering**: Search by artist, title, genre, or format
- **Sortable Columns**: Organize by any metadata field
- **Export Options**: Download filtered results as CSV

### How to Use:
1. **Browse**: Scroll through your complete collection
2. **Search**: Use the search box to find specific tracks
3. **Filter**: Click column headers to sort by different criteria
4. **Export**: Download results for offline analysis

### Understanding the Data:
- **Artist/Title/Album**: Basic track identification
- **Genre/BPM**: Musical characteristics
- **Format/Bitrate**: Technical file information
- **Duration**: Track length in minutes:seconds
- **File Location**: Where the track is stored

---

## 📀 Physical Collection Management

### Collection Expansion Process:
Your Discogs collection starts as a list of releases (albums). MusicTool expands these into individual tracks for detailed analysis.

### Step-by-Step Expansion:

#### 1. Initial Import
- Your Discogs CSV contains basic release information
- Each row represents one album/release
- Limited track-level detail available

#### 2. Expansion Process
1. **Go to Tools** → Collection Expansion
2. **Set Batch Size** (start with 10-50 for testing)
3. **Click "Start Expansion"**
4. **Monitor Progress** in real-time

#### 3. What Happens:
- MusicTool queries Discogs API for each release
- Extracts complete tracklist information
- Adds detailed metadata (label, catalog number, year)
- Stores everything in local database

#### 4. Progress Monitoring:
- **Real-time Updates**: See current processing status
- **Success/Error Counts**: Track expansion accuracy
- **ETA**: Estimated completion time
- **Batch Progress**: Current batch status

### Expected Results:
- **Input**: 594 releases (example)
- **Output**: 1,791+ individual tracks
- **Success Rate**: 95-98% typical
- **Processing Time**: 2-3 tracks per second

---

## 🔍 Gap Analysis

Gap Analysis helps you identify tracks in your physical collection that are missing from your digital library.

### Configuration Options:

#### Confidence Threshold (50-95%)
- **85% (Recommended)**: Good balance of accuracy and sensitivity
- **90%+**: Very strict, fewer false positives
- **80% or lower**: More sensitive, may include similar tracks

#### Analysis Modes:
- **🚀 Fast Sample (100 tracks)**: Quick preview for testing
- **🔍 Complete Analysis**: Process your entire collection
- **🎯 Custom Range**: Specify exact number of tracks

### How It Works:

#### 1. Intelligent Matching
- **Fuzzy String Matching**: Handles variations in track names
- **Multi-Factor Scoring**: Considers artist, title, and combined similarity
- **Performance Optimized**: Uses indexing for speed

#### 2. Confidence Scoring
- **Title Weight**: 60% (most important)
- **Artist Weight**: 30% 
- **Combined Weight**: 10%
- **Final Score**: Weighted average of all factors

#### 3. Match Categories:
- **Found** (≥ threshold): Track exists in digital collection
- **Missing** (< threshold): Track not found or low confidence match

### Reading Results:

#### Summary Metrics:
- **Found Percentage**: How much of your physical collection is digitized
- **Missing Count**: Tracks you might want to acquire digitally
- **Average Confidence**: Overall matching quality

#### Detailed Results:
- **Color Coding**: Green = found, Red = missing
- **Confidence Scores**: Numerical similarity ratings
- **Match Details**: See exactly which digital track matched

### Action Items:
1. **Review Missing Tracks**: Identify acquisition targets
2. **Check Low Confidence Matches**: Verify accuracy
3. **Export Results**: Download for offline review
4. **Prioritize by Album**: Focus on complete album gaps

---

## 🔄 Duplicate Finder

The Duplicate Finder helps clean up your digital collection by identifying potential duplicate tracks.

### Detection Methods:

#### 🎵 Artist + Title (Recommended)
- **Best For**: Finding true duplicates
- **How It Works**: Compares both artist and title with fuzzy matching
- **Accuracy**: Highest precision, lowest false positives

#### 🎼 Title Only
- **Best For**: Finding covers, remixes, different versions
- **How It Works**: Focuses only on track titles
- **Use Case**: Identify multiple versions of the same song

#### 📁 Filename Similarity
- **Best For**: Files with similar naming patterns
- **How It Works**: Compares actual file names
- **Use Case**: Detect duplicate downloads with different metadata

#### ⏱️ Duration + Title
- **Best For**: Identical recordings with different metadata
- **How It Works**: Combines title matching with track length
- **Use Case**: Same recording with different artist credits

### Configuration:

#### Similarity Threshold (60-95%)
- **85% (Recommended)**: Good balance for most collections
- **90%+**: Very strict, only obvious duplicates
- **80% or lower**: More sensitive, requires careful review

### Understanding Results:

#### Duplicate Groups:
- Each group contains potentially duplicate tracks
- **Original**: First track found (reference)
- **Duplicates**: Similar tracks with confidence scores

#### Quality Analysis:
- **File Size**: Larger files typically higher quality
- **Bitrate**: Higher bitrate = better audio quality
- **Format**: Lossless formats (FLAC) vs. compressed (MP3)

#### Space Savings:
- **Potential MB Saved**: Storage you could reclaim
- **Largest Groups**: Most duplicated tracks
- **Format Distribution**: Which file types have duplicates

### Recommended Workflow:

#### 1. Start Conservative
- Use 85-90% threshold initially
- Review results carefully
- Verify before deleting anything

#### 2. Quality Priority
- Keep highest bitrate versions
- Prefer lossless formats (FLAC > WAV > MP3)
- Consider file size as quality indicator

#### 3. Manual Review
- **Export Results**: Download duplicate lists
- **Check Samples**: Listen to suspected duplicates
- **Batch Process**: Handle duplicates systematically

#### 4. Safety First
- **Backup Important Files**: Before deletion
- **Test on Small Sets**: Start with obvious duplicates
- **Keep Originals**: If unsure, keep both copies

---

## ⚙️ Collection Tools

### Expansion Tool
**Purpose**: Convert Discogs releases into individual tracks

#### Settings:
- **Max Releases**: Control batch size (start small)
- **Progress Monitor**: Real-time status updates
- **Error Handling**: Automatic retry for failed requests

#### Best Practices:
- Start with 10-20 releases to test
- Monitor API rate limits (60 requests/minute)
- Run expansion during off-peak hours
- Check error logs for problematic releases

### Configuration Status
**Purpose**: Verify system setup and health

#### Checks:
- **API Key Status**: Verify Discogs connectivity
- **Database Health**: Confirm data integrity
- **File Locations**: Validate data file paths
- **System Performance**: Monitor processing speed

---

## 🎯 Workflow Recommendations

### For New Users:

#### Week 1: Setup & Exploration
1. **Day 1**: Complete initial setup, launch Dashboard
2. **Day 2**: Explore Digital and Physical collections
3. **Day 3**: Run small expansion test (50 releases)
4. **Day 4**: Try Gap Analysis on sample data
5. **Day 5**: Test Duplicate Finder on subset

#### Week 2: Full Analysis
1. **Expand Complete Collection**: Process all Discogs releases
2. **Full Gap Analysis**: Identify all missing tracks
3. **Comprehensive Duplicate Scan**: Clean up digital library
4. **Export and Review**: Download results for planning

### For DJ Collections:

#### Monthly Routine:
1. **Update Collections**: Export latest Traktor and Discogs data
2. **Run Gap Analysis**: Find new missing tracks
3. **Duplicate Cleanup**: Maintain clean digital library
4. **Acquisition Planning**: Prioritize missing track purchases

#### Pre-Gig Workflow:
1. **Verify Track Quality**: Check for duplicates and low-quality files
2. **Gap Check**: Ensure all planned tracks are digitized
3. **Export Playlists**: Use analysis results for set planning

### For Collectors:

#### Quarterly Reviews:
1. **Collection Growth**: Monitor dashboard statistics
2. **Genre Analysis**: Understand collection evolution
3. **Missing Track Reports**: Plan acquisition strategies
4. **Quality Audits**: Maintain high-standard digital library

---

## 🔧 Troubleshooting

### Common Issues:

#### "No API Key Found"
- **Solution**: Check `.env` file exists with correct key
- **Verify**: Key should be on line: `DISCOGS_API_KEY=your_key`

#### "Gap Analysis Taking Too Long"
- **Solution**: Use Sample Mode first (100 tracks)
- **Check**: Large collections require patience
- **Optimize**: Start with smaller confidence threshold

#### "Expansion Errors"
- **Common Cause**: API rate limiting
- **Solution**: Reduce batch size, wait between retries
- **Check**: Error logs for specific problematic releases

#### "No Digital Collection Found"
- **Solution**: Verify `.nml` file in `data/` folder
- **Check**: File exported correctly from Traktor
- **Alternative**: Try re-exporting collection

### Performance Tips:

#### For Large Collections (10,000+ tracks):
- Use Sample modes for initial testing
- Run analysis during off-peak hours
- Consider breaking into smaller batches
- Monitor system memory usage

#### For Better Accuracy:
- Clean metadata before import
- Use consistent naming conventions
- Verify file quality and completeness
- Regular database maintenance

---

## 📊 Understanding Your Results

### Gap Analysis Interpretation:

#### High Match Rates (85%+):
- **Excellent digitization coverage**
- Focus on remaining gaps
- Consider quality upgrades

#### Medium Match Rates (60-84%):
- **Significant digitization opportunity**
- Prioritize by artist/album
- Plan systematic acquisition

#### Low Match Rates (<60%):
- **Major digitization project needed**
- Start with favorite artists/albums
- Consider bulk acquisition strategies

### Duplicate Analysis Interpretation:

#### High Duplicate Rates (>20%):
- **Significant cleanup opportunity**
- Focus on space savings first
- Systematic quality improvements

#### Medium Duplicate Rates (10-20%):
- **Normal for active collections**
- Target obvious duplicates first
- Quality-based decision making

#### Low Duplicate Rates (<10%):
- **Well-maintained collection**
- Focus on edge cases
- Preventive measures for future

---

## 🎵 Best Practices

### Collection Management:
- **Regular Updates**: Monthly analysis runs
- **Quality First**: Prioritize high-bitrate files
- **Systematic Approach**: Process in logical batches
- **Documentation**: Keep records of changes

### Data Quality:
- **Consistent Naming**: Standardize artist/album names
- **Complete Metadata**: Fill in genre, year, label information
- **File Organization**: Logical folder structures
- **Backup Strategy**: Regular collection backups

### Analysis Workflow:
- **Start Small**: Test with samples first
- **Verify Results**: Manual spot checks
- **Incremental Changes**: Gradual improvements
- **Track Progress**: Monitor improvement over time

MusicTool is designed to grow with your collection and adapt to your workflow. Start with the basics and gradually explore advanced features as you become more comfortable with the system.
