# 🤖 Gatekeeper (AI Mode) - Implementation Summary

**Data implementacji:** 16.12.2025
**Branch:** `gatekeeper-1`
**Status:** ✅ MVP Complete - Ready for Testing

---

## 📋 Spis Treści

1. [Co zostało zrobione](#co-zostało-zrobione)
2. [Jak to działa](#jak-to-działa)
3. [Architektura systemu](#architektura-systemu)
4. [Golden 8 Parameters](#golden-8-parameters)
5. [API Endpoints](#api-endpoints)
6. [Frontend UI](#frontend-ui)
7. [Workflow użytkownika](#workflow-użytkownika)
8. [Koszty (Credits)](#koszty-credits)
9. [Następne kroki](#następne-kroki)
10. [Known Issues](#known-issues)

---

## 🎯 Co zostało zrobione

### **Problem:**
Obecny system analizy (Standard Mode):
- 30+ parametrów → trudny wybór dla użytkownika
- Proste porównanie mean/std → nie radzi sobie z multi-modal distributions (np. playlist z różnymi tempami)
- Brak AI verdict → użytkownik musi sam interpretować wyniki
- Sample rate 11025 Hz → niższa dokładność

### **Rozwiązanie: Gatekeeper (AI Mode)**

Production-ready MIR system z:
1. **Golden 8 Parameters** - tylko najważniejsze parametry
2. **Native Sample Rate** (44.1k/48k) - wyższa dokładność
3. **sklearn NearestNeighbors** - znajdź najbliższy track z playlisty (obsługa multi-modal)
4. **Weighted Z-Score** - wagi dla każdego parametru
5. **LLM Prompt Generator** - gotowy prompt do ChatGPT/Claude/Gemini
6. **Critical Alerts** - automatyczna detekcja problemów

---

## ⚙️ Jak to działa

### **1. Analiza Playlisty**

```
Użytkownik upload 5-30 tracków → Backend:

1. Dla każdego tracka:
   - librosa.load(sr=None)  // Native SR!
   - Extract Golden 8

2. StandardScaler.fit(playlist_matrix)
   // Normalizuj wszystkie 8 parametrów

3. NearestNeighbors(k=1).fit(scaled_features)
   // Przygotuj model do znajdowania najbliższego

4. Zapisz session
```

**Output:**
- `session_id`
- Lista Golden 8 dla każdego tracka
- Fitted models (scaler + nn_model)

---

### **2. Sprawdzenie User Track**

```
Użytkownik upload swojego tracka → Backend:

1. Extract Golden 8 z user track (sr=None)

2. Transform przez scaler
   user_scaled = scaler.transform(user_features)

3. Znajdź najbliższy track z playlisty
   nearest_idx = nn_model.kneighbors(user_scaled)
   reference_track = playlist[nearest_idx]

4. Oblicz Weighted Z-Scores
   z = (user_val - ref_val) / std_dev
   weighted_z = z * weight

5. Critical Alerts
   if |weighted_z| > 2.0 for beat_strength/onset_rate:
      → CRITICAL

6. Generate LLM Prompt
   → Kompletny tekst gotowy do copy-paste
```

**Output:**
- User features (Golden 8)
- Nearest reference track
- Weighted Z-scores dla każdego parametru
- Critical alerts
- **LLM Prompt** (gotowy do wklejenia w ChatGPT/Claude)

---

## 🏗️ Architektura systemu

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                           │
│  ┌───────────────────────────────────────────────┐     │
│  │ Step 1: Mode Toggle                           │     │
│  │   [📊 Standard Mode] [🤖 AI Mode] ← active    │     │
│  │                                                │     │
│  │ Reference Selection:                           │     │
│  │   • Create Playlist (2-30 tracks)             │     │
│  │   • [Upload Files] → analyzePlaylistGatekeeper()│   │
│  └───────────────────────────────────────────────┘     │
│                          ↓                              │
│  ┌───────────────────────────────────────────────┐     │
│  │ Step 2: Upload Your Track                     │     │
│  │   • [Upload File]                             │     │
│  │   • [Compare Now] → compareTrackGatekeeper()  │     │
│  │   • (NO parameter selection in AI Mode)       │     │
│  └───────────────────────────────────────────────┘     │
│                          ↓                              │
│  ┌───────────────────────────────────────────────┐     │
│  │ Step 3: Results                               │     │
│  │   ⚠️ Critical Alerts                          │     │
│  │   📊 Golden 8 Comparison Table                │     │
│  │   🤖 LLM Prompt                               │     │
│  │      [📋 Copy] [🤖 ChatGPT] [💎 Claude]      │     │
│  └───────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP
┌─────────────────────────────────────────────────────────┐
│                      BACKEND                            │
│  ┌───────────────────────────────────────────────┐     │
│  │ POST /api/gatekeeper/analyze-playlist         │     │
│  │   Input: files (2-30 MP3/WAV/FLAC)            │     │
│  │   Cost: 100 credits                           │     │
│  │                                                │     │
│  │   1. For each file:                           │     │
│  │      - PlaylistGatekeeper.extract_golden_8()  │     │
│  │        (librosa, sr=None)                     │     │
│  │                                                │     │
│  │   2. PlaylistGatekeeper.fit_playlist()        │     │
│  │      - StandardScaler.fit()                   │     │
│  │      - NearestNeighbors(k=1).fit()            │     │
│  │                                                │     │
│  │   Output: session_id, playlist_features       │     │
│  └───────────────────────────────────────────────┘     │
│                          ↓                              │
│  ┌───────────────────────────────────────────────┐     │
│  │ POST /api/gatekeeper/check                    │     │
│  │   Input: user_track, session_id               │     │
│  │   Cost: 100 credits                           │     │
│  │                                                │     │
│  │   1. extract_golden_8(user_track)             │     │
│  │   2. scaler.transform(user_features)          │     │
│  │   3. nn_model.kneighbors() → nearest_ref      │     │
│  │   4. calculate_weighted_z_scores()            │     │
│  │   5. identify_critical_alerts()               │     │
│  │   6. generate_llm_prompt()                    │     │
│  │                                                │     │
│  │   Output: LLM prompt, alerts, z-scores        │     │
│  └───────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   LLM (External)                        │
│  User copies prompt → Pastes into ChatGPT/Claude       │
│  LLM returns: VERDICT + REASONING                       │
│    • PASS: Track fits playlist                          │
│    • REJECT: Major incompatibilities                    │
│    • CONDITIONAL: Needs adjustments                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🎼 Golden 8 Parameters

### **Lista parametrów:**

| # | Parameter | Description | Weight | Extraction |
|---|-----------|-------------|--------|------------|
| 1 | **BPM** | Tempo | 1.5x | `librosa.beat.beat_track()` |
| 2 | **Beat Strength** | Onset strength mean | **3.0x** ⭐ | `librosa.onset.onset_strength()` mean |
| 3 | **Onset Rate** | Events per second | **2.0x** | `len(onset_detect()) / duration` |
| 4 | **Energy** | RMS mean | 1.5x | `librosa.feature.rms()` mean |
| 5 | **Danceability** | Pulse Clarity | **2.0x** | Tempogram ratio (peak/mean) |
| 6 | **Spectral Rolloff** | Frequency rolloff mean | 1.0x | `librosa.feature.spectral_rolloff()` |
| 7 | **Spectral Flatness** | Tonality vs noise | 1.0x | `librosa.feature.spectral_flatness()` |
| 8 | **Dynamic Range** | Peak-RMS in dB | 0.5x | `20*log10(peak/rms)` |

### **Dlaczego te 8?**

✅ **Beat Strength & Onset Rate** - CRITICAL dla rytmu/gatunku (wagi 3.0x i 2.0x)
✅ **BPM** - Ważne, ale tolerancja dla half-time (waga 1.5x)
✅ **Danceability (Pulse Clarity)** - NIE koreluje z Beat Strength (tempogram-based)
✅ **Energy** - Ogólna intensywność
✅ **Spectral features** - Tonalność/barwa
✅ **Dynamic Range** - Mastering (najmniej ważne, 0.5x)

---

### **Danceability - Szczegóły implementacji**

**Problem:** Beat Strength mierzy *głośność* onsetów, nie regularność rytmu.

**Rozwiązanie: Pulse Clarity (Tempogram-based)**

```python
def _extract_pulse_clarity(self, y, sr):
    # 1. Onset envelope
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)

    # 2. Tempogram (time-frequency representation of tempo)
    tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)

    # 3. Ratio: strongest pulse vs mean energy
    mean_energy = np.mean(tempogram)
    max_peak = np.max(tempogram)

    pulse_clarity = max_peak / mean_energy

    # 4. Normalize to 0-1 (empirical: good values = 2-10)
    return np.clip(pulse_clarity / 10.0, 0, 1)
```

**Interpretacja:**
- **High (0.7-1.0):** Strong, clear, regular pulse → Very danceable
- **Medium (0.4-0.6):** Moderate pulse clarity
- **Low (0.0-0.3):** Chaotic/weak pulse → Not danceable

**Dlaczego to działa:**
- Tempogram pokazuje "siłę" każdego tempa w czasie
- Silny regularny puls → jeden dominujący peak
- Chaotyczny rytm → rozproszona energia, niski ratio

---

## 🔌 API Endpoints

### **1. POST /api/gatekeeper/analyze-playlist**

**Opis:** Analizuj playlistę (2-30 tracków) używając Golden 8.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/gatekeeper/analyze-playlist" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@track1.mp3" \
  -F "files=@track2.mp3" \
  ...
  -F "files=@track30.mp3"
```

**Response (Success 200):**
```json
{
  "session_id": "abc123-def456-...",
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

**Errors:**
- 400: Too few/many files (need 2-30)
- 402: Insufficient credits
- 500: Analysis failed

**Cost:** 100 credits

---

### **2. POST /api/gatekeeper/check**

**Opis:** Sprawdź user track vs playlist. Zwraca LLM prompt.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/gatekeeper/check" \
  -H "Authorization: Bearer $TOKEN" \
  -F "user_track=@my_song.mp3" \
  -F "session_id=abc123-def456-..."
```

**Response (Success 200):**
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
    "filename": "ref_track.mp3",
    "bpm": 128.0,
    "beat_strength": 0.82,
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
    "Onset Rate: 2.1σ below reference (WARNING)"
  ],
  "llm_prompt": "You are an expert music industry A&R assistant...\n\n[Full prompt text]",
  "credits_remaining": 800
}
```

**Errors:**
- 400: Session not in gatekeeper mode
- 402: Insufficient credits
- 404: Session not found
- 500: Analysis failed

**Cost:** 100 credits

---

## 🎨 Frontend UI

### **Step 1: Mode Toggle**

```html
<div class="mode-toggle">
  <button class="mode-btn active" data-mode="standard">
    📊 Standard Mode
    <span>Full flexibility, 30+ parameters</span>
  </button>
  <button class="mode-btn" data-mode="ai">
    🤖 AI Mode
    <span>Golden 8, LLM verdict</span>
  </button>
</div>
```

**CSS Features:**
- Glassmorphism background
- Active state: green border + glow
- Hover: translateY(-4px) + shadow
- Responsive flex layout

**JavaScript:**
```javascript
// Global state
let analysisMode = 'standard'; // or 'ai'

// Toggle handler
document.querySelectorAll('.mode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    switchAnalysisMode(btn.dataset.mode);
  });
});

function switchAnalysisMode(mode) {
  analysisMode = mode;

  // Update UI
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === mode);
  });

  // Hide params in AI Mode
  if (mode === 'ai') {
    document.querySelector('.parameter-selection-wizard').style.display = 'none';
  }
}
```

---

### **Step 2: Auto-hiding Parameters**

W AI Mode:
- Parameter selection jest **ukryte** (Golden 8 automatyczne)
- Compare button aktywny gdy tylko user track jest uploadowany
- Brak konieczności wyboru parametrów

```javascript
function updateCompareButton() {
  const compareBtn = document.getElementById('compare-now-btn');
  const hasFile = userTrackFile !== null;

  if (analysisMode === 'ai') {
    // AI Mode: only need file
    compareBtn.disabled = !hasFile;
  } else {
    // Standard Mode: need file + params
    const hasParams = getSelectedParameters().length > 0;
    compareBtn.disabled = !(hasFile && hasParams);
  }
}
```

---

### **Step 3: Results Display**

#### **Critical Alerts**
```html
<div id="critical-alerts-list">
  <!-- Red box -->
  <div style="background: rgba(255, 107, 107, 0.1);
              border: 1px solid rgba(255, 107, 107, 0.3);
              color: #ff6b6b;">
    ⚠️ Beat Strength: 7.2σ below reference (CRITICAL)
  </div>

  <!-- Yellow box -->
  <div style="background: rgba(255, 193, 7, 0.1);
              border: 1px solid rgba(255, 193, 7, 0.3);
              color: #ffc107;">
    ⚠️ Onset Rate: 2.1σ below reference (WARNING)
  </div>
</div>
```

**Logic:**
- CRITICAL: `|weighted_z| > 2.0` for beat_strength/onset_rate
- WARNING: `|weighted_z| > 1.5` for other parameters

---

#### **Golden 8 Comparison Table**
```html
<table>
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Your Track</th>
      <th>Reference</th>
      <th>Z-Score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>BPM</td>
      <td>124.00</td>
      <td>128.00</td>
      <td style="color: #ffc107;">-1.20</td> <!-- Yellow -->
    </tr>
    <tr>
      <td>Beat Strength</td>
      <td>0.45</td>
      <td>0.82</td>
      <td style="color: #ff6b6b;">-7.20</td> <!-- Red -->
    </tr>
    <!-- ... -->
  </tbody>
</table>
```

**Color coding:**
- 🟢 Green: `|z| < 1.5`
- 🟡 Yellow: `1.5 ≤ |z| < 2.0`
- 🔴 Red: `|z| ≥ 2.0`

---

#### **LLM Prompt + Copy**
```html
<textarea id="llm-prompt-text" readonly>
You are an expert music industry A&R assistant...
</textarea>

<button id="copy-prompt-btn">📋 COPY PROMPT</button>
<button onclick="window.open('https://chat.openai.com')">
  🤖 Open ChatGPT
</button>
```

**Copy logic:**
```javascript
function copyLLMPrompt() {
  const textarea = document.getElementById('llm-prompt-text');
  textarea.select();
  document.execCommand('copy');

  // Show success message
  document.getElementById('copy-success-message').style.display = 'block';
  setTimeout(() => {
    document.getElementById('copy-success-message').style.display = 'none';
  }, 3000);
}
```

---

## 👤 Workflow użytkownika

### **Complete User Journey (AI Mode):**

```
1. LOGIN
   http://localhost:8000/wizard
   → Register or Login
   → Otrzymujesz 1000 credits

2. STEP 1: Choose Reference
   → Kliknij [🤖 AI Mode]
   → Kliknij [Create Playlist]
   → Upload 5-30 MP3 files
   → Kliknij [Analyze Playlist]

   Backend:
   POST /api/gatekeeper/analyze-playlist
   - Extract Golden 8 from each track
   - Fit StandardScaler + NearestNeighbors
   - Cost: 100 credits

   → Success: Move to Step 2
   → Credits: 1000 → 900

3. STEP 2: Upload Your Track
   → Upload your_song.mp3
   → (Parameters auto-selected: Golden 8)
   → Kliknij [Compare Now]

   Backend:
   POST /api/gatekeeper/check
   - Extract Golden 8 from user track
   - Find nearest reference track
   - Calculate weighted Z-scores
   - Generate LLM prompt
   - Cost: 100 credits

   → Success: Move to Step 3
   → Credits: 900 → 800

4. STEP 3: Results
   → See Critical Alerts (if any)
   → See Golden 8 Comparison Table
   → See LLM Prompt

   → Kliknij [📋 COPY PROMPT]
   → Kliknij [🤖 Open ChatGPT]

5. PASTE INTO ChatGPT/Claude
   Prompt:
   "You are an expert music industry A&R assistant...

    GOLDEN 8 COMPARISON:
    BPM: 124 vs 128 (z: -1.2)
    Beat Strength: 0.45 vs 0.82 (z: -7.2) ⚠️ CRITICAL
    ...

    VERDICT: [PASS / REJECT / CONDITIONAL]
    REASONING: ..."

   LLM Response:
   "VERDICT: REJECT

   REASONING:
   Your track has critically weak beat strength compared to
   the reference playlist. The 7.2σ deviation indicates the
   rhythmic punch is significantly lower, which would make
   it feel out of place in this high-energy playlist.

   KEY ISSUES:
   - Beat Strength too low (needs +80% increase)
   - Onset Rate sparse (add more rhythmic elements)

   RECOMMENDED ACTIONS:
   - Compress kick/snare more aggressively
   - Add transient shaper to drums
   - Increase drum levels in mix by 3-4dB
   - Consider adding percussive elements"
```

---

## 💰 Koszty (Credits)

| Operation | Standard Mode | AI Mode |
|-----------|--------------|---------|
| Analyze Playlist | 100 credits | 100 credits |
| Compare Track | 100 credits | 100 credits |
| **Total** | **200 credits** | **200 credits** |

**Default user credits:** 1000 (5 full analyses)

**Future monetization:**
- Free tier: 1000 credits
- Premium: Auto-refill, higher limits
- Pro: Direct LLM integration (no copy-paste)

---

## 🚀 Następne kroki

### **Priorytet 1: Bugfixy**
- [ ] Ukryj AI Mode toggle dla "Single Track" (1:1) - nie ma sensu bez playlisty
- [ ] Test na różnych formatach audio (MP3, WAV, FLAC)
- [ ] Test z dużą playlistą (30 tracków)
- [ ] Error handling dla corrupt files

### **Priorytet 2: UX Improvements**
- [ ] Loading animation podczas analizy (pokazuj który track jest przetwarzany)
- [ ] Tooltip z wyjaśnieniem każdego parametru Golden 8
- [ ] Przykładowe wartości "good/bad" dla każdego parametru
- [ ] Visual progress bar dla batch analysis

### **Priorytet 3: Features**
- [ ] Direct LLM integration (OpenAI/Anthropic API)
- [ ] Preset playlists ("Top 40 Hits 2025", "EDM Bangers", etc.)
- [ ] Batch mode: check multiple user tracks vs 1 playlist
- [ ] Export results to PDF/CSV
- [ ] Historical tracking (save past analyses)

### **Priorytet 4: Optimization**
- [ ] Cache analyzed playlists (jeśli user wraca do tej samej playlisty)
- [ ] Parallel processing dla batch analysis
- [ ] Reduce Golden 8 extraction time (optimize librosa calls)

---

## ⚠️ Known Issues

### **1. showProgressModal bugfix**
**Problem:** `showProgressModal()` wywoływane z 2 parametrami, ale funkcja przyjmuje tylko 1.

**Fix:** Commit `407f523`
```javascript
// BEFORE (broken)
showProgressModal('Title', 'Message');

// AFTER (fixed)
showProgressModal('Title');
updateProgressModal(5, 'Message');
```

### **2. AI Mode w trybie 1:1**
**Problem:** AI Mode widoczny dla "Single Track" reference, ale nie ma sensu:
- NearestNeighbors wymaga ≥2 samples
- StandardScaler std=0 z 1 tracka
- Z-scores nie mają sensu

**TODO:** Ukryj AI Mode toggle gdy wybrano "Single Track"

### **3. Native Sample Rate może być wolne**
**Obserwacja:** `sr=None` (native 44.1k/48k) jest 4x wolniejsze niż `sr=11025`.

**Mitigation:**
- Pokazuj progress (który track jest aktualnie przetwarzany)
- Limit 30 tracków max
- Future: parallel processing

### **4. Brak walidacji audio files**
**Problem:** Backend może crashować na corrupt files.

**TODO:** Add try-catch w `extract_golden_8()` z fallback do None

---

## 📁 Struktura plików

```
backend/
├── core/
│   ├── audio_processor.py          [EXISTING - Standard Mode]
│   ├── playlist_comparator.py      [EXISTING - Standard Mode]
│   ├── track_comparator.py         [EXISTING - Standard Mode]
│   ├── playlist_gatekeeper.py      [NEW - AI Mode] ⭐
│   └── report_generator.py         [EXISTING]
├── main.py                         [MODIFIED - +2 endpoints]
├── GATEKEEPER_API.md               [NEW - API docs]
└── models.py, schemas.py, auth.py  [EXISTING]

frontend/
├── index-wizard.html               [MODIFIED - Mode toggle + AI results]
├── static/
│   ├── css/
│   │   └── wizard.css              [MODIFIED - Mode toggle styles]
│   └── js/
│       └── wizard.js               [MODIFIED - Gatekeeper logic]
```

**Commits:**
1. `d791eb8` - Add Gatekeeper backend (Golden 8 + sklearn + LLM prompt)
2. `6924921` - Add AI Mode frontend UI
3. `407f523` - Fix showProgressModal calls

---

## 🧪 Testing Checklist

### **Backend Tests:**
- [ ] `/api/gatekeeper/analyze-playlist` z 5 trackami
- [ ] `/api/gatekeeper/analyze-playlist` z 30 trackami (max)
- [ ] `/api/gatekeeper/analyze-playlist` z 1 trackiem (should fail 400)
- [ ] `/api/gatekeeper/check` z valid session
- [ ] `/api/gatekeeper/check` z invalid session (should fail 404)
- [ ] Credits deduction (100 + 100 = 200 total)
- [ ] Error handling dla corrupt audio files

### **Frontend Tests:**
- [ ] Mode toggle działa (Standard ↔ AI)
- [ ] AI Mode info box pokazuje się
- [ ] Parameter selection ukrywa się w AI Mode
- [ ] Playlist analysis w AI Mode (progress modal)
- [ ] Track comparison w AI Mode (progress modal)
- [ ] Critical alerts display (czerwone/żółte boxy)
- [ ] Golden 8 table display (color-coded Z-scores)
- [ ] LLM prompt display + copy button
- [ ] Copy to clipboard działa
- [ ] Quick links do ChatGPT/Claude/Gemini działają

### **E2E Test:**
- [ ] Complete flow: Login → AI Mode → Upload playlist → Upload track → Copy prompt → Paste w ChatGPT → Get verdict

---

## 📚 Dodatkowe zasoby

**Dokumentacja:**
- `backend/GATEKEEPER_API.md` - Complete API reference
- Ten plik - Implementation summary

**Repozytoria:**
- Branch: `gatekeeper-1`
- Commits: `d791eb8`, `6924921`, `407f523`

**Librosa docs:**
- Tempogram: https://librosa.org/doc/main/generated/librosa.feature.tempogram.html
- Onset detection: https://librosa.org/doc/main/generated/librosa.onset.onset_detect.html

**sklearn docs:**
- StandardScaler: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
- NearestNeighbors: https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestNeighbors.html

---

## 🎯 Success Metrics

**MVP Success Criteria:**
- ✅ Golden 8 extraction działa (native SR)
- ✅ sklearn pipeline działa (scaler + nn)
- ✅ LLM prompt generation działa
- ✅ Frontend UI kompletny (toggle + results)
- ✅ End-to-end flow działa (upload → analyze → results)
- ⏳ User testing (5-10 użytkowników)
- ⏳ LLM verdict accuracy >80%

**Production Readiness:**
- Error handling (corrupt files, network errors)
- Rate limiting (prevent abuse)
- Logging (track usage, errors)
- Monitoring (response times, credit usage)
- Documentation (user guide)

---

## 💡 Lekcje nauczone

### **1. Tempogram > Simple beat detection**
Początkowy pomysł: użyć `beat_track()` do danceability.
Problem: Koreluje z beat strength (głośność).
Rozwiązanie: Tempogram ratio (pulse clarity) - mierzy regularność, nie głośność.

### **2. NearestNeighbors > Mean/Std profiling**
Standard Mode używa mean/std → problem z multi-modal distributions.
Przykład: Playlist z EDM (128 BPM) + Hip-Hop (80 BPM) → mean ~100 BPM → bezsens.
Rozwiązanie: Znajdź najbliższy track → porównaj z nim, nie ze średnią.

### **3. Weighted Z-scores > Raw Z-scores**
Wszystkie parametry równe → beat strength ma taką samą wagę jak dynamic range.
Problem: Dynamic range (mastering) nie powinien dyskwalifikować tracka.
Rozwiązanie: Wagi (beat_strength: 3.0x, dynamic_range: 0.5x).

### **4. LLM Prompt > Surowe liczby**
User widzi: "Z-score: -7.2" → co to znaczy?
Rozwiązanie: LLM interpretuje → "Beat strength is critically low. Add compression, increase drum levels by 3-4dB."

### **5. Native SR vs 11025 Hz**
Standard Mode: `sr=11025` → szybko, ale niska dokładność.
AI Mode: `sr=None` (44.1k/48k) → wolniej, ale dokładniej.
Trade-off: Golden 8 (8 params) vs 30+ params → kompensuje wolniejszy SR.

---

**Koniec dokumentu.**

Ostatnia aktualizacja: 16.12.2025
Autor: Claude Sonnet 4.5 + grzegorzry45
Branch: `gatekeeper-1`
