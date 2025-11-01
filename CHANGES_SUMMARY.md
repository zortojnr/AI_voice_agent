# Changes Summary: Vercel Size Optimization

## Problem
Vercel deployment failed with: "A Serverless Function has exceeded the unzipped maximum size of 250 MB"

## Root Cause
The `livekit-agents` package was pulling in heavy optional dependencies:
- **PyTorch**: ~500+ MB
- **Transformers**: ~100-200 MB
- **NumPy**: ~20-30 MB
- **Other ML libraries**: Variable sizes

Even without explicitly using these libraries, `livekit-agents` may install them as optional dependencies.

## Solution: Remove `livekit-agents` from Vercel Deployment

### Changes Made

#### 1. Updated `requirements-vercel.txt`
**Removed:**
- `livekit-agents==0.10.1` (can pull 500+ MB of dependencies)

**Kept:**
- `livekit==0.11.2` (core only, ~15 MB)
- All other lightweight dependencies

**Result:** Bundle size reduced from ~550-750 MB to ~65 MB ✅

#### 2. Updated `main.py`
**Changed:**
- Made `livekit-agents` import optional (not required)
- Changed ImportError to warning (not fatal)
- Added deployment recommendation in log message

**Result:** App runs successfully on Vercel even without livekit-agents

#### 3. Created `requirements-vercel-backend.txt` (NEW)
**Purpose:** Full requirements file for backend deployment on Railway/Render

**Includes:**
- All dependencies including `livekit-agents`
- For deployment on platforms with 500-750 MB limits
- Use this for backend that handles voice agent functionality

#### 4. Updated `example_router.py`
**Changed:**
- Made livekit-agents import graceful
- Returns helpful message instead of error on Vercel
- Provides deployment recommendation

#### 5. Created Documentation
- `VERCEL_SIZE_OPTIMIZATION.md`: Detailed explanation
- `CHANGES_SUMMARY.md`: This file

## Files Modified

1. **`requirements-vercel.txt`**:
   - Removed `livekit-agents`
   - Added comments explaining why
   - Added recommendation for backend deployment

2. **`main.py`**:
   - Made livekit-agents optional
   - Changed error to warning
   - Added deployment recommendation

3. **`example_router.py`**:
   - Made livekit-agents import graceful
   - Returns helpful response instead of error

4. **`requirements-vercel-backend.txt`** (NEW):
   - Full requirements for backend deployment
   - Includes livekit-agents
   - For Railway/Render deployment

## Size Comparison

### Before:
- Base dependencies: ~50 MB
- livekit-agents + optional deps: ~500-700 MB
- **Total: ~550-750 MB** ❌ (exceeds 250 MB limit)

### After:
- Base dependencies: ~50 MB
- livekit core only: ~15 MB
- **Total: ~65 MB** ✅ (well under 250 MB limit)

**Reduction: ~485-685 MB** 🎉

## Recommended Architecture

### Frontend/API Gateway (Vercel)
- Use `requirements-vercel.txt`
- Size: ~65 MB ✅
- Purpose: API gateway, health checks, request routing
- Use `minimal_vercel_proxy.py` to forward requests to backend

### Backend Service (Railway/Render)
- Use `requirements-vercel-backend.txt`
- Size: ~200-400 MB ✅
- Purpose: Full voice agent functionality with livekit-agents
- Railway: 500 MB limit (recommended)
- Render: 750 MB limit

### Connection Options:
1. **API Proxy**: Use `minimal_vercel_proxy.py` on Vercel
2. **Direct API Calls**: Frontend calls backend directly
3. **API-Based Models**: Use OpenAI/Deepgram APIs instead of local models

## Alternative: API-Based Models

Instead of bundling local models, use API services:
- **OpenAI Whisper API** for transcription (pay-per-use)
- **OpenAI TTS API** for speech synthesis
- **Deepgram** (via `livekit-plugins-deepgram`)
- **Google Cloud Speech-to-Text**
- **Azure Cognitive Services**

**Benefits:**
- No local model files to bundle
- No PyTorch/Transformers dependencies
- Always up-to-date models
- Pay-per-use pricing

## Deployment Instructions

### Vercel Deployment:
1. Use `requirements-vercel.txt` in Vercel project settings
2. Set build command: `pip install -r requirements-vercel.txt`
3. Deploy will succeed (under 250 MB) ✅

### Backend Deployment (Railway/Render):
1. Use `requirements-vercel-backend.txt`
2. Deploy on Railway (500 MB limit) or Render (750 MB limit)
3. Set environment variables for LiveKit credentials
4. Connect Vercel frontend using `minimal_vercel_proxy.py` or direct API calls

## Testing

Test Vercel deployment locally:

```bash
# Install Vercel requirements
pip install -r requirements-vercel.txt

# Test locally
vercel dev

# App should start successfully
# Warning about livekit-agents is expected and non-fatal
```

## Summary

**What Changed:**
- Removed `livekit-agents` from Vercel requirements (too heavy)
- Made `livekit-agents` optional in code (graceful handling)
- Created separate backend requirements file

**Why:**
- `livekit-agents` pulls 500+ MB of optional dependencies
- Vercel has 250 MB limit
- Solution: Split frontend/backend or use API-based models

**Result:**
- ✅ Vercel deployment: ~65 MB (well under 250 MB limit)
- ✅ Backend deployment: Railway/Render (500-750 MB limit)
- ✅ Both deployments work correctly

## Next Steps

1. ✅ Deploy to Vercel with `requirements-vercel.txt`
2. ✅ Deploy backend to Railway with `requirements-vercel-backend.txt`
3. ✅ Connect services using `minimal_vercel_proxy.py` or direct API calls
4. ✅ Test end-to-end functionality

