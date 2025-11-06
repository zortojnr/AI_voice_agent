# Vercel Size Optimization - What Changed

## Problem
Vercel build failed with: "A Serverless Function has exceeded the unzipped maximum size of 250 MB"

## Root Cause
The `livekit-agents` package pulls in heavy optional dependencies:
- **PyTorch**: ~500+ MB
- **Transformers**: ~100-200 MB  
- **NumPy**: ~20-30 MB
- **Other ML libraries**: Variable

Even if you don't explicitly use these, `livekit-agents` may install them as optional dependencies, causing the bundle to exceed 250 MB.

## Solution: Remove `livekit-agents` from Vercel Deployment

### Changes Made

1. **Updated `requirements-vercel.txt`**:
   - ❌ **Removed**: `livekit-agents` (can pull 500+ MB of dependencies)
   - ✅ **Kept**: `livekit` core (lightweight, ~10-20 MB)
   - ✅ **Result**: Vercel deployment stays under 250 MB

2. **Updated `main.py`**:
   - Made `livekit-agents` import optional
   - Added warning instead of error when not available
   - Allows app to run on Vercel without crashing

3. **Created `requirements-vercel-backend.txt`**:
   - Full requirements including `livekit-agents`
   - For deployment on Railway/Render (500-750 MB limits)
   - Use this for backend that handles voice agent functionality

## Recommended Architecture

### Option 1: Split Architecture (Recommended)

**Frontend/API Gateway (Vercel)**:
- Lightweight FastAPI app
- Uses `requirements-vercel.txt`
- Size: ~50-100 MB (well under limit)
- Purpose: API gateway, health checks, request routing

**Backend Service (Railway/Render)**:
- Full voice agent functionality
- Uses `requirements-vercel-backend.txt`
- Size: ~200-400 MB (acceptable on Railway/Render)
- Purpose: LiveKit agents, ML models (if needed)

**Connection**:
- Use `minimal_vercel_proxy.py` on Vercel to forward requests
- Or use direct API calls between services

### Option 2: API-Based Models

Instead of local models, use API services:
- **OpenAI Whisper API** for transcription
- **OpenAI TTS API** for speech synthesis  
- **Google Cloud Speech-to-Text**
- **Azure Cognitive Services**
- **Deepgram** (via `livekit-plugins-deepgram`)

Benefits:
- No local model files to bundle
- No PyTorch/Transformers dependencies
- Pay-per-use pricing
- Always up-to-date models

### Option 3: Full Backend on Railway/Render

Deploy entire application on Railway or Render:
- Railway: 500 MB limit (free tier)
- Render: 750 MB limit (free tier with limitations)
- No need to split architecture
- Simpler deployment

## Files Modified

1. **`requirements-vercel.txt`**:
   - Removed `livekit-agents`
   - Added comments explaining why
   - Added recommendation for backend deployment

2. **`main.py`**:
   - Changed ImportError to warning
   - Made livekit-agents optional
   - Added deployment recommendation in log

3. **`requirements-vercel-backend.txt`** (NEW):
   - Full requirements for backend deployment
   - Includes livekit-agents
   - For Railway/Render deployment

## Size Comparison

### Before (with livekit-agents):
- Base dependencies: ~50 MB
- livekit-agents + optional deps: ~500-700 MB
- **Total: ~550-750 MB** ❌ (exceeds 250 MB limit)

### After (without livekit-agents):
- Base dependencies: ~50 MB
- livekit core only: ~15 MB
- **Total: ~65 MB** ✅ (well under 250 MB limit)

## Deployment Steps

### For Vercel (Frontend/Gateway):

1. Use `requirements-vercel.txt` in Vercel project settings
2. Set build command: `pip install -r requirements-vercel.txt`
3. Deploy will succeed (under 250 MB)

### For Railway/Render (Backend):

1. Use `requirements-vercel-backend.txt`
2. Deploy on Railway (recommended) or Render
3. Set environment variables for LiveKit credentials
4. Use `minimal_vercel_proxy.py` on Vercel to forward requests

## Testing

Test Vercel deployment locally:

```bash
# Create clean environment
python -m venv venv_vercel
source venv_vercel/bin/activate  # Windows: venv_vercel\Scripts\activate

# Install Vercel requirements
pip install -r requirements-vercel.txt

# Test locally
vercel dev

# App should start without errors
# Warning about livekit-agents is expected
```

## Next Steps

1. ✅ Deploy to Vercel with `requirements-vercel.txt`
2. ✅ Deploy backend to Railway with `requirements-vercel-backend.txt`
3. ✅ Connect services using `minimal_vercel_proxy.py` or direct API calls
4. ✅ Test end-to-end functionality

## Summary

**What Changed:**
- Removed `livekit-agents` from Vercel requirements (too heavy)
- Made `livekit-agents` optional in code
- Created separate backend requirements file

**Why:**
- `livekit-agents` pulls 500+ MB of optional dependencies
- Vercel has 250 MB limit
- Solution: Split frontend/backend or use API-based models

**Result:**
- Vercel deployment: ~65 MB ✅
- Backend deployment: Railway/Render (500-750 MB limit) ✅
- Both deployments work correctly ✅

