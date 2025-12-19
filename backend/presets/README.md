# System Presets Directory

This directory contains official/factory presets that are available to all users without authentication.

## How to Add a New Preset

### 1. Prepare Your Preset JSON File

Your preset file should follow this format:

```json
{
  "name": "Your Preset Name",
  "profile": {
    "mode": "gatekeeper",
    "tracks": [
      {
        "bpm": 120.5,
        "beat_strength": 1.2,
        "onset_rate": 4.5,
        "energy": 0.75,
        "danceability": 0.8,
        "spectral_rolloff": 5000.0,
        "spectral_flatness": 0.002,
        "dynamic_range": 10.5,
        "filename": "track1.mp3"
      },
      {
        "bpm": 125.0,
        ...
      }
    ]
  },
  "analysis": [],
  "timestamp": "2025-12-18T00:00:00.000Z",
  "exported_at": "2025-12-18T00:00:00.000Z"
}
```

**Required fields in each track:**
- `bpm` - Tempo (beats per minute)
- `beat_strength` - Beat strength/intensity
- `onset_rate` - Onset rate (events per second)
- `energy` - RMS energy (0-1)
- `danceability` - Danceability score (0-1)
- `spectral_rolloff` - Spectral rolloff frequency
- `spectral_flatness` - Spectral flatness (0-1)
- `dynamic_range` - Dynamic range in dB
- `filename` - Original filename (for reference)

### 2. Save the Preset File

Save your preset JSON file in this directory with a descriptive name:
```
backend/presets/your_preset_name.json
```

Use lowercase with underscores for the filename:
- `spotify_dance_2025.json` ✓
- `Spotify Dance 2025.json` ✗

### 3. Update the Presets Index

Edit `presets_index.json` and add your preset to the `presets` array:

```json
{
  "presets": [
    {
      "id": "your_preset_id",
      "name": "🎵 Your Preset Display Name",
      "description": "Brief description of your preset",
      "tracks_count": 100,
      "file": "your_preset_name.json",
      "created_at": "2025-12-18",
      "tags": ["genre", "style", "mood"]
    }
  ]
}
```

**Field descriptions:**
- `id` - Unique identifier (use lowercase with underscores)
- `name` - Display name with emoji (shown in UI)
- `description` - Brief description (1-2 sentences)
- `tracks_count` - Number of tracks in the preset
- `file` - Filename of the JSON file (must match step 2)
- `created_at` - Creation date (YYYY-MM-DD format)
- `tags` - Array of descriptive tags

### 4. Test Your Preset

1. Restart the backend server
2. Open the application
3. Go to "Use Popular Playlist" section
4. Your preset should appear in "🏆 Official Algorithms"
5. Click "Load" to test if it works correctly

## API Endpoints

Presets are served through these endpoints:

- `GET /api/system-presets` - Returns list of all presets (metadata only)
- `GET /api/system-presets/{preset_id}` - Returns full preset data

## File Size Considerations

- Each preset with 100 tracks is approximately 50-60KB
- 10-20 presets = 500KB-1.2MB total
- All presets are loaded on-demand (only metadata is loaded at startup)
- Keep individual preset files under 100KB when possible

## Example Preset IDs

Good IDs:
- `spotify_dance_2025`
- `techno_berlin_underground`
- `lofi_study_beats`
- `commercial_pop_hits`

Bad IDs:
- `Spotify Dance 2025` (has spaces)
- `my-preset` (use underscores, not dashes)
- `preset1` (not descriptive enough)

## Naming Conventions

**Preset Names (displayed to users):**
- Use emoji for visual appeal: 🎵 🎹 🎧 🎤 🔊 ☕ 🏆
- Keep it under 40 characters
- Examples: "🎵 Spotify Dance (2025)", "🎹 Techno Bunker"

**File Names (internal):**
- Use lowercase
- Use underscores instead of spaces
- Include year if relevant
- Examples: `spotify_dance_2025.json`, `techno_bunker.json`

## Troubleshooting

**Preset doesn't appear in UI:**
- Check if `presets_index.json` is valid JSON
- Verify the `id` in index matches the actual file name (without .json)
- Restart the backend server

**Error when loading preset:**
- Check if preset JSON file is valid
- Verify all tracks have required fields (bpm, beat_strength, etc.)
- Check browser console for error messages

**Preset loads but doesn't work:**
- Verify `mode: "gatekeeper"` is present in profile
- Check that tracks array is not empty
- Ensure all numeric values are valid (not NaN or Infinity)
