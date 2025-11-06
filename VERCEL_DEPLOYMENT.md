# Vercel Deployment Guide

## Problem: Size Limit Exceeded

Vercel has a 250 MB unzipped size limit for Serverless Functions. The `livekit-agents` package can pull in heavy dependencies like PyTorch, Transformers, and other ML libraries that exceed this limit.

## Solution: Optimized Deployment

### 1. Use Optimized Requirements

For Vercel deployment, use `requirements-vercel.txt` instead of `requirements.txt`:

```bash
# In your Vercel project settings, specify:
# Build Command: pip install -r requirements-vercel.txt
```

Or create a `vercel.json` that automatically uses the optimized file.

### 2. Files Excluded from Deployment

The `vercel.json` configuration excludes:
- **Virtual environments**: `venv/`, `.venv/`, `env/`
- **Cache directories**: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- **Test files**: `tests/`, `test_*.py`, `*_test.py`
- **Model files**: `*.pt`, `*.bin`, `*.onnx`, `*.pth`, `*.h5`, `*.pb`, `*.ckpt`
- **Large data directories**: `models/`, `data/`, `datasets/`, `checkpoints/`
- **Development files**: `.vscode/`, `.idea/`, `*.md`, `docs/`
- **Log files**: `*.log`, `logs/`

### 3. Dependency Optimizations

#### Removed/Replaced:
- **`uvicorn[standard]`** → **`uvicorn`** (removed extras like `watchfiles`, `websockets`)
- **`structlog`** → **Python stdlib `logging`** (smaller footprint)

#### Pinned Versions:
- Specific versions in `requirements-vercel.txt` to avoid pulling in newer heavy dependencies

#### LiveKit Agents:
- `livekit-agents` is kept but may still pull optional dependencies
- Consider using API-based voice agent services instead of bundling models

### 4. Recommended Architecture Split

If the project still exceeds 250 MB after optimization, split it:

#### **Frontend (Vercel)**:
- Static assets
- API proxy/forwarding
- Lightweight endpoints

#### **Backend (Alternative Hosting)**:

**Option A: Railway** (Recommended for Python)
- ✅ Supports up to 500 MB
- ✅ Automatic deployments from GitHub
- ✅ Free tier available
- ✅ Native Python support

**Option B: Render**
- ✅ Supports up to 750 MB
- ✅ Free tier with limitations
- ✅ Good Python support
- ✅ Easy setup

**Option C: Fly.io**
- ✅ Supports large applications
- ✅ Global edge deployment
- ✅ Free tier available

**Option D: AWS Lambda + API Gateway**
- ✅ Serverless with 10 GB limit (layers)
- ⚠️ More complex setup
- ✅ Pay-per-use pricing

### 5. LiveKit-Specific Considerations

If you need `livekit-agents` with ML models:

1. **Use External Model APIs**: Instead of bundling models, call external APIs:
   - OpenAI Whisper API for transcription
   - OpenAI TTS API for speech synthesis
   - Google Cloud Speech-to-Text
   - Azure Cognitive Services

2. **Split Agent Service**: Deploy the LiveKit agent separately:
   - Agent service on Railway/Render (handles ML models)
   - API service on Vercel (handles HTTP requests)

3. **Use Lightweight Plugins**: Use LiveKit plugins that don't require local models:
   - `livekit-plugins-openai` (API-based)
   - `livekit-plugins-deepgram` (API-based)

### 6. Testing Locally

Test the optimized build locally:

```bash
# Create a virtual environment
python -m venv venv_vercel
source venv_vercel/bin/activate  # On Windows: venv_vercel\Scripts\activate

# Install optimized requirements
pip install -r requirements-vercel.txt

# Test with vercel dev
vercel dev
```

### 7. Vercel Configuration

In your Vercel project dashboard:

1. **Environment Variables**: Add all required `.env` variables
2. **Build Command**: `pip install -r requirements-vercel.txt`
3. **Output Directory**: Leave empty (not a static site)
4. **Install Command**: Leave empty (build command handles it)
5. **Python Version**: Set to `3.13` or match your local version

### 8. Alternative: Minimal Vercel Deployment

If you still need to deploy on Vercel, create a minimal proxy that forwards to your backend:

```python
# minimal_api.py - Lightweight Vercel deployment
from fastapi import FastAPI
import httpx

app = FastAPI()

BACKEND_URL = "https://your-backend.railway.app"  # Your backend URL

@app.get("/{path:path}")
async def proxy(path: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/{path}")
        return response.json()
```

This keeps Vercel deployment under 10 MB while routing to a larger backend.

## Summary

- ✅ Use `requirements-vercel.txt` for optimized dependencies
- ✅ `vercel.json` excludes unnecessary files
- ✅ Consider splitting frontend/backend architecture
- ✅ Use API-based ML services instead of bundling models
- ✅ Railway or Render recommended for backend hosting

