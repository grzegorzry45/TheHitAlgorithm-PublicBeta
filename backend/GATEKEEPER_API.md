# Gatekeeper API Documentation

## Overview

The **Gatekeeper** (AI Mode) is a production-ready MIR system that checks if a user track fits a playlist profile using the "Golden 8" audio parameters.

### Key Features:
- ✅ **Golden 8 Parameters Only** (fast analysis, ~5-10s per track)
- ✅ **Native Sample Rate** (sr=None for accuracy)
- ✅ **sklearn-based Analysis** (StandardScaler + NearestNeighbors)
- ✅ **Weighted Z-Score Deviation**
- ✅ **LLM Prompt Generation** (copy-paste into ChatGPT/Claude/Gemini)
- ✅ **Critical Alerts** for rhythm features

---

## Golden 8 Parameters

1. **BPM** (Tempo)
2. **Beat Strength** (mean onset strength)
3. **Onset Rate** (rhythmic events per second)
4. **Energy** (RMS mean)
5. **Danceability** (Pulse Clarity via Tempogram)
6. **Spectral Rolloff** (mean, 85th percentile)
7. **Spectral Flatness** (mean)
8. **Dynamic Range** (Peak-RMS in dB)

### Feature Weights (for Weighted Z-Score):
```python
{
    'beat_strength': 3.0,    # CRITICAL for genre vibe
    'onset_rate': 2.0,       # Important for density
    'bpm': 1.5,              # Important (allows half-time)
    'energy': 1.5,
    'danceability': 2.0,     # Important for groove
    'spectral_rolloff': 1.0,
    'spectral_flatness': 1.0,
    'dynamic_range': 0.5     # Least important (mastering)
}
```

---

## API Endpoints

### 1. Analyze Playlist (Gatekeeper)

**Endpoint:** `POST /api/gatekeeper/analyze-playlist`

**Description:** Analyze a playlist (2-30 tracks) using Golden 8 only.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/gatekeeper/analyze-playlist" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@track1.mp3" \
  -F "files=@track2.mp3" \
  -F "files=@track3.mp3"
```

**Response:**
```json
{
  "session_id": "abc123...",
  "tracks_analyzed": 25,
  "errors": [],
  "playlist_features": [
    {
      "filename": "track1.mp3",
      "bpm": 128.0,
      "beat_strength": 0.82,
      "onset_rate": 4.5,
      "energy": 0.71,
      "danceability": 0.65,
      "spectral_rolloff": 4500.0,
      "spectral_flatness": 0.12,
      "dynamic_range": 12.5
    },
    ...
  ],
  "credits_remaining": 900,
  "message": "Gatekeeper playlist analysis complete"
}
```

**Cost:** 100 credits

---

### 2. Check User Track (Gatekeeper)

**Endpoint:** `POST /api/gatekeeper/check`

**Description:** Check if a user track fits the analyzed playlist. Returns LLM prompt.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/gatekeeper/check" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "user_track=@my_song.mp3" \
  -F "session_id=abc123..."
```

**Response:**
```json
{
  "session_id": "abc123...",
  "user_filename": "my_song.mp3",
  "user_features": {
    "bpm": 124.0,
    "beat_strength": 0.45,
    "onset_rate": 3.2,
    "energy": 0.65,
    "danceability": 0.58,
    "spectral_rolloff": 4200.0,
    "spectral_flatness": 0.15,
    "dynamic_range": 11.8
  },
  "nearest_reference": {
    "filename": "reference_track.mp3",
    "bpm": 128.0,
    "beat_strength": 0.82,
    "onset_rate": 4.5,
    ...
  },
  "weighted_z_scores": {
    "bpm": {
      "user_value": 124.0,
      "ref_value": 128.0,
      "z_score": -0.8,
      "weighted_z": -1.2,
      "weight": 1.5
    },
    "beat_strength": {
      "user_value": 0.45,
      "ref_value": 0.82,
      "z_score": -2.4,
      "weighted_z": -7.2,
      "weight": 3.0
    },
    ...
  },
  "critical_alerts": [
    "Beat Strength: 7.2σ below reference (CRITICAL)",
    "Onset Rate: 2.6σ below reference (WARNING)"
  ],
  "llm_prompt": "You are an expert music industry A&R assistant...\n\n[Full LLM prompt text ready to copy-paste]",
  "credits_remaining": 800
}
```

**Cost:** 100 credits

---

## LLM Prompt Format

The `llm_prompt` field contains a complete, ready-to-use prompt for LLMs (ChatGPT, Claude, Gemini).

### Example Prompt:

```
You are an expert music industry A&R assistant specializing in playlist curation.

Your task: Analyze whether a submitted track fits a specific playlist profile.

CONTEXT:
The track has been analyzed against a playlist's sonic signature using the "Golden 8" audio parameters...

---

GOLDEN 8 COMPARISON (User Track vs Closest Reference):

BPM:
  User: 124.00
  Reference: 128.00
  Weighted Z-Score: -1.20 (weight: 1.5x)

Beat Strength:
  User: 0.45
  Reference: 0.82
  Weighted Z-Score: -7.20 (weight: 3.0x)

[... all 8 parameters ...]

---

⚠️ CRITICAL ALERTS:
  • Beat Strength: 7.2σ below reference (CRITICAL)
  • Onset Rate: 2.6σ below reference (WARNING)

---

INSTRUCTIONS:
1. Evaluate the track based on:
   - Overall similarity to the reference track
   - Critical rhythm features (Beat Strength, Onset Rate) - these are MOST important
   - Genre/playlist context

2. Provide a verdict: [PASS / REJECT / CONDITIONAL]

3. Explain your reasoning in 2-3 sentences

FORMAT YOUR RESPONSE:

VERDICT: [PASS / REJECT / CONDITIONAL]

REASONING:
[Your analysis here]

KEY ISSUES (if any):
[List specific problems]

RECOMMENDED ACTIONS (if CONDITIONAL):
[Specific mixing/production suggestions]
```

---

## Usage Flow (MVP)

### Step 1: Analyze Playlist
```bash
# Upload 15-30 reference tracks
curl -X POST "http://localhost:8000/api/gatekeeper/analyze-playlist" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@ref1.mp3" \
  -F "files=@ref2.mp3" \
  ... \
  -F "files=@ref30.mp3"

# Save session_id from response
SESSION_ID="abc123..."
```

### Step 2: Check Your Track
```bash
# Upload your track
curl -X POST "http://localhost:8000/api/gatekeeper/check" \
  -H "Authorization: Bearer $TOKEN" \
  -F "user_track=@my_song.mp3" \
  -F "session_id=$SESSION_ID"

# Copy the llm_prompt field from response
```

### Step 3: Get AI Verdict
1. Copy the `llm_prompt` text
2. Open ChatGPT/Claude/Gemini
3. Paste the prompt
4. Get expert A&R verdict: **PASS / REJECT / CONDITIONAL**

---

## Frontend Integration (TODO)

The frontend UI will be added in a future update:
- [ ] Toggle: "Standard Mode" vs "AI Mode"
- [ ] Golden 8 display (no parameter selection in AI Mode)
- [ ] LLM Prompt display with copy button
- [ ] Quick links to ChatGPT/Claude/Gemini
- [ ] Results visualization

---

## Technical Details

### Danceability (Pulse Clarity)

Unlike traditional danceability, **Pulse Clarity** measures rhythmic regularity without correlation to beat loudness:

```python
def _extract_pulse_clarity(self, y, sr):
    # Compute tempogram
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)

    # Ratio of highest peak to mean energy
    mean_energy = np.mean(tempogram)
    max_peak = np.max(tempogram)

    if mean_energy > 0:
        pulse_clarity = max_peak / mean_energy
        # Normalize to 0-1 (empirically, good values: 2-10)
        return np.clip(pulse_clarity / 10.0, 0, 1)

    return 0.0
```

- **High value (0.7-1.0):** Strong, clear, regular pulse (highly danceable)
- **Low value (0.0-0.3):** Chaotic or weak pulse (less danceable)

### sklearn Pipeline

```python
# 1. Fit StandardScaler on playlist
scaler = StandardScaler()
scaled_features = scaler.fit_transform(playlist_matrix)

# 2. Fit NearestNeighbors (k=1)
nn_model = NearestNeighbors(n_neighbors=1, metric='euclidean')
nn_model.fit(scaled_features)

# 3. Find nearest reference for user track
user_scaled = scaler.transform(user_array)
distances, indices = nn_model.kneighbors(user_scaled)
nearest_ref = playlist_features[indices[0][0]]

# 4. Calculate Weighted Z-Score
z_score = (user_val - ref_val) / std_dev
weighted_z = z_score * weight
```

---

## Credits Cost

| Operation | Cost |
|-----------|------|
| Analyze Playlist (2-30 tracks) | 100 credits |
| Check User Track | 100 credits |

**Total per analysis:** 200 credits

---

## Future Enhancements

- [ ] Auto-LLM integration (direct API calls to OpenAI/Anthropic)
- [ ] Batch checking (multiple user tracks at once)
- [ ] Preset playlists (Top 40 Hits 2025, EDM Bangers, etc.)
- [ ] Visual comparison charts
- [ ] Historical tracking (save previous checks)

---

## Example: Complete Workflow

```python
import requests

# 1. Login
auth_response = requests.post('http://localhost:8000/auth/login', data={
    'username': 'user@example.com',
    'password': 'password'
})
token = auth_response.json()['access_token']

headers = {'Authorization': f'Bearer {token}'}

# 2. Analyze playlist
files = [
    ('files', open('playlist/track1.mp3', 'rb')),
    ('files', open('playlist/track2.mp3', 'rb')),
    # ... 15-30 files
]

playlist_response = requests.post(
    'http://localhost:8000/api/gatekeeper/analyze-playlist',
    headers=headers,
    files=files
)

session_id = playlist_response.json()['session_id']

# 3. Check user track
with open('my_song.mp3', 'rb') as f:
    check_response = requests.post(
        'http://localhost:8000/api/gatekeeper/check',
        headers=headers,
        files={'user_track': f},
        data={'session_id': session_id}
    )

result = check_response.json()

# 4. Copy LLM prompt
llm_prompt = result['llm_prompt']
print(llm_prompt)

# Now paste into ChatGPT/Claude for verdict!
```

---

## Testing

```bash
# Run backend
cd backend
python main.py

# Test endpoints with sample tracks
# (Full test suite TBD)
```

---

## Questions?

Contact: [your-email@example.com]
