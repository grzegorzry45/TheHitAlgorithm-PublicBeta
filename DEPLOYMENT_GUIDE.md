# Deployment Guide - The Algorithm Web App

## Quick Start (3 Steps to Deploy!)

### Step 1: Prepare Your Code

Your web app is ready in the `web/` folder! The structure is:
```
web/
├── backend/         # FastAPI server
├── frontend/        # HTML/CSS/JS interface
├── render.yaml      # Deployment config
└── README.md        # Full documentation
```

### Step 2: Push to GitHub

1. Create a new GitHub repository
2. Initialize git in the `web/` folder:

```bash
cd web
git init
git add .
git commit -m "Initial commit - The Algorithm web app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/the-algorithm-web.git
git push -u origin main
```

### Step 3: Deploy to Render (FREE!)

1. Go to https://render.com and sign up (free account)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your repository
5. Render will auto-detect `render.yaml` configuration
6. Click **"Create Web Service"**

**That's it!** Your app will be live in ~5 minutes at:
`https://the-algorithm-[random].onrender.com`

---

## Alternative: Manual Render Configuration

If auto-detection doesn't work:

**Settings:**
- **Name**: `the-algorithm`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Branch**: `main`

---

## Testing Locally (Optional)

Want to test before deploying?

### Install Dependencies:
```bash
cd web/backend
pip install -r requirements.txt
```

### Run Server:
```bash
cd web/backend
python main.py
```

### Open Browser:
```
http://localhost:8000
```

---

## How to Use the Web App

### 1. Analyze Playlist Tab
- Upload 15-30 tracks from your target playlist
- Click "ANALYZE PLAYLIST"
- View sonic profile (BPM, energy, loudness, etc.)

### 2. Your Library Tab
- Upload your tracks
- Click "ANALYZE & COMPARE"
- Get recommendations for each track

### 3. Compare Tab
- **Playlist Mode**: Compare 1 track vs entire playlist
- **Track Mode**: Compare 2 tracks directly (1:1)
- Get detailed side-by-side analysis

### 4. Recommendations Tab
- View AI-generated suggestions
- Export HTML report with all recommendations

---

## Render Free Tier Features

✅ **Included:**
- 512 MB RAM
- Free SSL (HTTPS)
- Automatic deploys from GitHub
- Custom domain support

⚠️ **Limitations:**
- Spins down after 15 min inactivity (first request takes ~30 sec)
- Temporary file storage (files deleted on restart)
- 15 min build timeout

💡 **Tip**: For production use with high traffic, upgrade to paid tier ($7/month)

---

## Updating Your App

After making changes:

```bash
git add .
git commit -m "Update features"
git push
```

Render automatically deploys new changes!

---

## Troubleshooting

### "Module not found" error
- Run: `pip install -r backend/requirements.txt`

### Files disappear after deployment
- Render uses ephemeral storage
- Download reports immediately after generation
- For persistent storage, add AWS S3 (future enhancement)

### Out of memory on Render
- Use MP3 files instead of WAV (smaller)
- Analyze max 25 tracks instead of 30
- Or upgrade to paid tier for more RAM

### First request is slow
- Render free tier spins down after inactivity
- First request wakes it up (~30 seconds)
- Subsequent requests are instant

---

## Next Steps (Future Enhancements)

1. **Add Database**: Store analysis results (PostgreSQL)
2. **User Auth**: Login system for saved sessions
3. **Spotify API**: Auto-fetch audio features
4. **WebSockets**: Real-time progress updates
5. **Cloud Storage**: S3 for persistent file storage
6. **Custom Domain**: Point your domain to Render

---

## Support

Questions? Issues? Check:
- `web/README.md` - Full technical documentation
- Render docs: https://render.com/docs
- FastAPI docs: https://fastapi.tiangolo.com

---

Built with FastAPI + Vanilla JS • No frameworks needed!
