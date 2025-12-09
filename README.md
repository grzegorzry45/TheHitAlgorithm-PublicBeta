# The Algorithm - Web Version

Web version of The Algorithm - Audio Playlist Analyzer

## Features

- **Target Playlist Analysis**: Upload 15-30 tracks to create a sonic profile
- **Batch Track Comparison**: Compare your music library against the target
- **Single Track Compare**:
  - Compare vs entire playlist profile
  - 1:1 track comparison with AI recommendations
- **AI Recommendations**: Get actionable suggestions for each parameter
- **HTML Reports**: Export detailed reports with all recommendations
- **Futuristic Dark UI**: Terminal-style interface with clean design

## Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- librosa - Audio analysis engine
- pyloudnorm - Loudness metering
- numpy - Numerical computations

**Frontend:**
- Vanilla JavaScript (no frameworks needed!)
- CSS3 with custom dark theme
- Drag & drop file uploads

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup

1. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the development server:
```bash
cd backend
python main.py
```

3. Open browser to `http://localhost:8000`

The frontend is served automatically by FastAPI.

## File Structure

```
TheSpotifyAlgorithm-web/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── core/                # Audio analysis logic
│   │   ├── audio_processor.py
│   │   ├── comparator.py
│   │   ├── track_comparator.py
│   │   └── report_generator.py
│   ├── uploads/             # Temporary file storage
│   ├── reports/             # Generated HTML reports
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Main page
│   └── static/
│       ├── css/
│       │   └── style.css    # Dark futuristic theme
│       └── js/
│           └── app.js       # Frontend logic
└── README.md
```

## API Endpoints

### Upload & Analysis
- `POST /api/upload/playlist` - Upload playlist files (15-30 tracks)
- `POST /api/upload/user-tracks` - Upload your tracks
- `POST /api/analyze/playlist` - Analyze playlist and create profile

### Comparison
- `POST /api/compare/batch` - Compare all user tracks vs playlist
- `POST /api/compare/single` - Compare single track (playlist or 1:1 mode)

### Reports
- `POST /api/report/generate` - Generate HTML report
- `GET /api/report/download/{session_id}` - Download report

### Utility
- `GET /health` - Health check
- `DELETE /api/session/{session_id}` - Clean up session data

## Usage

1. **Analyze Playlist Tab**:
   - Drag & drop 15-30 MP3/WAV files from target playlist
   - Click "ANALYZE PLAYLIST"
   - View sonic profile

2. **Your Library Tab**:
   - Upload your tracks
   - Click "ANALYZE & COMPARE"
   - Auto-switches to Recommendations tab

3. **Compare Tab**:
   - Upload your track
   - Choose mode:
     - "vs Playlist" - Compare against playlist profile
     - "1:1 Track Compare" - Upload reference track for direct comparison
   - Click "COMPARE TRACKS"

4. **Recommendations Tab**:
   - View AI-generated suggestions
   - Export HTML report

## Future Enhancements

- User authentication & sessions
- Spotify API integration (auto-fetch audio features)
- Database for storing analysis results
- WebSocket for real-time progress
- ML model for playlist acceptance prediction

## License

MIT License

## Credits

Built from desktop PyQt6 app using Claude Code
