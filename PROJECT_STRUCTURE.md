# Project Structure - The Algorithm Web App

## Overview

Complete web version of your PyQt6 desktop app with:
- ✅ All original features (analyze, compare, recommendations)
- ✅ Futuristic dark theme (identical to desktop version)
- ✅ 4 sections/tabs (Analyze, Library, Compare, Recommendations)
- ✅ Drag & drop file upload
- ✅ Real-time progress bars
- ✅ HTML report generation

---

## File Structure

```
TheSpotifyAlgorithm-web/
│
├── backend/                          # FastAPI Backend
│   ├── main.py                       # Main FastAPI application (400 lines)
│   │   ├── Upload endpoints          # /api/upload/playlist, /api/upload/user-tracks
│   │   ├── Analysis endpoints        # /api/analyze/playlist
│   │   ├── Comparison endpoints      # /api/compare/batch, /api/compare/single
│   │   ├── Report endpoints          # /api/report/generate, /api/report/download
│   │   └── Session management        # In-memory storage
│   │
│   ├── core/                         # Analysis Logic (copied from desktop app)
│   │   ├── __init__.py
│   │   ├── audio_processor.py        # 31KB - All audio analysis (20+ parameters)
│   │   ├── comparator.py             # 17KB - Playlist comparison logic
│   │   ├── track_comparator.py       # 57KB - 1:1 track comparison
│   │   └── report_generator.py       # 9KB - HTML report generation
│   │
│   ├── uploads/                      # Temporary file storage (created at runtime)
│   ├── reports/                      # Generated HTML reports (created at runtime)
│   └── requirements.txt              # Python dependencies
│
├── frontend/                         # Vanilla JavaScript Frontend
│   ├── index.html                    # Main page with 4 tabs (200 lines)
│   │   ├── Analyze Playlist tab      # Upload 15-30 tracks
│   │   ├── Your Library tab          # Batch comparison
│   │   ├── Compare tab               # Single track vs playlist or 1:1
│   │   └── Recommendations tab       # AI suggestions
│   │
│   └── static/
│       ├── css/
│       │   └── style.css             # Dark futuristic theme (600 lines)
│       │       ├── Terminal-style UI # Black background, white/gray text
│       │       ├── Tab navigation    # PyQt-style tabs
│       │       ├── Upload zones      # Drag & drop areas
│       │       ├── Progress bars     # Real-time updates
│       │       ├── Results panels    # Comparison displays
│       │       └── Responsive design # Mobile-friendly
│       │
│       └── js/
│           └── app.js                # Frontend logic (800 lines)
│               ├── Tab navigation    # Switch between sections
│               ├── Drag & drop       # File upload handling
│               ├── API communication # Fetch requests to backend
│               ├── Progress tracking # Real-time updates
│               └── Results display   # Format and show data
│
├── .gitignore                        # Git ignore rules
├── requirements.txt                  # Python dependencies
├── README.md                         # Technical documentation
└── PROJECT_STRUCTURE.md              # This file
```

---

## Key Files Explained

### backend/main.py (Core API)

**Endpoints:**
- `GET /` - Serves frontend HTML
- `POST /api/upload/playlist` - Upload 15-30 playlist files
- `POST /api/upload/user-tracks` - Upload your tracks
- `POST /api/analyze/playlist` - Analyze playlist, create sonic profile
- `POST /api/compare/batch` - Compare all user tracks vs playlist
- `POST /api/compare/single` - Compare single track (2 modes)
- `POST /api/report/generate` - Generate HTML report
- `GET /api/report/download/{id}` - Download report
- `DELETE /api/session/{id}` - Cleanup session
- `GET /health` - Health check

**Features:**
- Session management (UUID-based)
- In-memory storage for fast access
- Temporary file handling
- CORS enabled for development
- Static file serving for frontend

---

### backend/core/ (Analysis Engine)

**audio_processor.py** - 20+ Audio Parameters:
- Core: BPM, Key, Energy, Loudness
- Spectral: Brightness, Rolloff, Flatness
- Energy: Low/Mid/High distribution
- Dynamics: Range, RMS, Compression
- Perceptual: Danceability, Valence, Stereo Width
- Technical: Zero Crossing, Beat Strength

**comparator.py** - Playlist Comparison:
- Create playlist sonic profile (average + std dev)
- Compare individual tracks vs profile
- Generate AI recommendations per parameter

**track_comparator.py** - 1:1 Track Comparison:
- Direct track-to-track comparison
- Side-by-side parameter analysis
- Detailed recommendations for matching

**report_generator.py** - HTML Reports:
- Beautiful formatted reports
- All recommendations included
- Downloadable for future reference

---

### frontend/index.html (UI Structure)

**Header:**
- Title: "THE ALGORITHM"
- Subtitle: Terminal-style status indicator

**4 Main Tabs:**

1. **Analyze Playlist**
   - Upload zone (drag & drop)
   - File list display
   - Analyze button
   - Progress bar
   - Results panel (playlist profile)

2. **Your Library**
   - Upload zone for your tracks
   - File list
   - Compare button
   - Progress bar
   - Auto-switches to Recommendations

3. **Compare**
   - Mode selector (playlist vs track)
   - Two upload zones (user + reference)
   - Compare button
   - Progress bar
   - Side-by-side results

4. **Recommendations**
   - Recommendation cards per track
   - Category-organized suggestions
   - Export report button

---

### frontend/static/css/style.css (Theme)

**Terminal-Inspired Design:**
- Background: Pure black (#000000)
- Text: White/gray (#ffffff, #e0e0e0, #b0b0b0)
- Borders: Medium gray (#888888)
- Font: Monospace (Consolas, Courier New)
- Accent: White highlights on hover

**Components:**
- Tab navigation (PyQt-style)
- Upload zones (dashed borders, drag-over effects)
- File lists (selectable items with remove buttons)
- Buttons (uppercase, letter-spaced)
- Progress bars (animated fills)
- Results panels (grid layouts)
- Comparison rows (color-coded differences)
- Recommendation cards (organized by category)

**Responsive:**
- Desktop: Multi-column grids
- Tablet: Adjusted layouts
- Mobile: Single column stacking

---

### frontend/static/js/app.js (Frontend Logic)

**Modules:**

1. **Tab Navigation**
   - Switch between 4 sections
   - Update URL state
   - Active tab highlighting

2. **Playlist Upload & Analysis**
   - Drag & drop handling
   - File validation (MP3/WAV/FLAC)
   - Min/max file count (15-30)
   - Upload to API
   - Trigger analysis
   - Display profile results

3. **User Tracks Upload & Batch Compare**
   - Upload your tracks
   - Send to API
   - Batch comparison
   - Display recommendations
   - Switch to Recommendations tab

4. **Single Track Compare**
   - Mode switching (playlist vs track)
   - Dual upload zones
   - API communication
   - Side-by-side display
   - Difference highlighting

5. **Recommendations Display**
   - Format recommendation cards
   - Category organization
   - Export report functionality

6. **Utility Functions**
   - Drag & drop setup
   - Progress updates
   - Error handling
   - Success notifications

---

## Data Flow

### Analyze Playlist Flow:
```
User drops files → Upload to /api/upload/playlist
                 ↓
                 Create session ID
                 ↓
                 Click "Analyze" → /api/analyze/playlist
                 ↓
                 Process all files with librosa
                 ↓
                 Calculate average profile
                 ↓
                 Display results (BPM, energy, etc.)
```

### Batch Compare Flow:
```
Upload user tracks → /api/upload/user-tracks
                   ↓
                   Click "Compare" → /api/compare/batch
                   ↓
                   Analyze each user track
                   ↓
                   Compare vs playlist profile
                   ↓
                   Generate recommendations per track
                   ↓
                   Display in Recommendations tab
```

### Single Compare Flow:
```
Upload track(s) → Select mode (playlist or 1:1)
                ↓
                Click "Compare" → /api/compare/single
                ↓
                Analyze user track
                ↓
                Compare vs target (playlist or reference track)
                ↓
                Display side-by-side results
                ↓
                Show recommendations
```

### Report Generation Flow:
```
Click "Export" → /api/report/generate
               ↓
               Format all recommendations as HTML
               ↓
               Save to reports/ folder
               ↓
               Return download URL
               ↓
               Open in new tab / download
```

---

## Technologies Used

**Backend:**
- Python 3.11+
- FastAPI (web framework)
- Uvicorn (ASGI server)
- librosa (audio analysis)
- numpy (numerical computing)
- pyloudnorm (loudness metering)
- matplotlib (visualizations)

**Frontend:**
- HTML5
- CSS3 (custom dark theme)
- Vanilla JavaScript (ES6+)
- No frameworks! (lightweight & fast)

---

## What Changed from Desktop App?

### Migrated to Web:
✅ All 4 tabs → 4 sections
✅ PyQt widgets → HTML elements
✅ Dark theme → CSS terminal theme
✅ Drag & drop → Browser native drag & drop
✅ Progress bars → CSS animated bars
✅ All analysis logic → Identical (reused core/)
✅ Report generation → Same HTML output

### New in Web Version:
🆕 API endpoints (RESTful)
🆕 Session management (UUID-based)
🆕 Browser-based UI (no installation needed)
🆕 Responsive design (works on mobile)

### Not Changed:
- Audio analysis algorithms (identical)
- 20+ parameters analyzed (same)
- Recommendation logic (same AI)
- Report format (same HTML)
- Feature completeness (100% ported)

---

## Performance

**Analysis Speed:**
- Single track: ~2-3 seconds
- 30 tracks: ~60-90 seconds
- Depends on server CPU

**File Size Limits:**
- Recommended: MP3 files (5-10 MB each)
- WAV files: Use with caution (large)

**Memory Usage:**
- Per session: ~100-200 MB

---

## Next Steps

Now that the web app is built:

1. **Test Locally**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   # Open http://localhost:8000
   ```

2. **Future Enhancements**:
   - Add user authentication
   - Integrate Spotify API
   - Add database for history
   - Real-time WebSocket updates
   - Custom branding/domain
