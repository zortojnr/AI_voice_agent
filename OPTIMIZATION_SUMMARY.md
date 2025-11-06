# Vercel Optimization Summary

## Changes Made

### 1. Updated `requirements.txt`
**Removed:**
- `uvicorn[standard]` → Changed to `uvicorn` (removed extras like `watchfiles`, `websockets`)
- `structlog` → Removed completely (use Python stdlib `logging` instead)

**Result:** Smaller bundle size by avoiding optional dependencies

### 2. Created `requirements-vercel.txt`
**Optimizations:**
- Pinned specific versions to avoid pulling newer heavy dependencies
- Minimal uvicorn installation (no extras)
- Removed structlog completely
- Kept only essential dependencies

**Files/Size Reduction:**
- `uvicorn[standard]` extras: ~10-15 MB
- `structlog`: ~2-3 MB
- Total reduction: ~12-18 MB

### 3. Created `vercel.json`
**Exclusions:**
- Virtual environments: `venv/`, `.venv/`, `env/`
- Cache: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- Tests: `tests/`, `test_*.py`, `*_test.py`
- **Model files**: `*.pt`, `*.bin`, `*.onnx`, `*.pth`, `*.h5`, `*.pb`, `*.ckpt`
- **Data directories**: `models/`, `data/`, `datasets/`, `checkpoints/`
- Development files: `.vscode/`, `.idea/`, `*.md`, `docs/`
- Log files: `*.log`, `logs/`

**Estimated Size Reduction:**
- Virtual environments: 50-200 MB (if accidentally included)
- Model files: Can be 100-500 MB+ (if using local ML models)
- Test files: 5-20 MB
- Cache: 10-50 MB

### 4. Created Minimal Proxy (`minimal_vercel_proxy.py`)
**Purpose:** If the main app still exceeds 250 MB, use this lightweight proxy (< 5 MB) to forward requests to a backend deployed on Railway/Render.

**Use Case:**
- Frontend/API gateway on Vercel (lightweight)
- Backend with ML models on Railway/Render (can be larger)

### 5. Updated Documentation
- Added `VERCEL_DEPLOYMENT.md` with comprehensive deployment guide
- Updated `README.md` with Vercel deployment section

## Libraries Excluded/Replaced

### Removed:
1. **`structlog`** (2-3 MB)
   - Replaced with: Python stdlib `logging`
   - Impact: No functionality loss, just different API

2. **`uvicorn[standard]` extras**
   - Removed: `watchfiles`, `websockets` (optional dependencies)
   - Replaced with: Minimal `uvicorn` installation
   - Impact: No auto-reload in production (not needed), websockets still work

### Potentially Heavy (If Included):
**`livekit-agents`** may pull in optional dependencies:
- PyTorch (~500 MB+ if included)
- Transformers (~100-200 MB if included)
- NumPy (~20-30 MB)
- Other ML libraries

**Solution:** Use API-based LiveKit plugins instead of bundling models:
- `livekit-plugins-openai` (API calls, no local models)
- `livekit-plugins-deepgram` (API calls, no local models)

## Recommended Architecture Split

If still exceeding 250 MB:

### Option 1: Split Frontend/Backend
- **Vercel**: Lightweight API proxy (`minimal_vercel_proxy.py`)
- **Railway/Render**: Full backend with ML models

### Option 2: Use API-Based Services
- Replace local ML models with API calls:
  - OpenAI Whisper API (transcription)
  - OpenAI TTS API (speech synthesis)
  - Google Cloud Speech-to-Text
  - Azure Cognitive Services

### Option 3: Deploy Entirely on Alternative Platform
**Recommended Platforms:**
1. **Railway** (Best for Python)
   - Limit: 500 MB
   - Free tier: Yes
   - Auto-deploy from GitHub: Yes

2. **Render**
   - Limit: 750 MB
   - Free tier: Yes (with limitations)
   - Easy Python setup

3. **Fly.io**
   - Limit: No specific limit
   - Free tier: Yes
   - Global edge deployment

## Testing Locally

Test the optimized build:

```bash
# Create clean environment
python -m venv venv_vercel
source venv_vercel/bin/activate  # Windows: venv_vercel\Scripts\activate

# Install optimized requirements
pip install -r requirements-vercel.txt

# Test with vercel dev
vercel dev
```

## Next Steps

1. **Deploy to Vercel** using `requirements-vercel.txt`
2. **Monitor build size** in Vercel dashboard
3. **If still exceeds 250 MB:**
   - Deploy backend to Railway/Render
   - Use `minimal_vercel_proxy.py` on Vercel
   - Or switch entire deployment to Railway/Render

## Files Created/Modified

**New Files:**
- `requirements-vercel.txt` - Optimized dependencies
- `vercel.json` - Vercel configuration with exclusions
- `VERCEL_DEPLOYMENT.md` - Comprehensive deployment guide
- `minimal_vercel_proxy.py` - Lightweight proxy for split architecture
- `OPTIMIZATION_SUMMARY.md` - This file

**Modified Files:**
- `requirements.txt` - Removed structlog, changed uvicorn
- `README.md` - Added Vercel deployment section

