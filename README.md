# Voice Agent Project

A production-ready voice agent built with LiveKit, FastAPI, and Python 3.13.

## Features

- ✅ Python 3.13 compatible (patches `lk_blingfire` import issue)
- ✅ Pure-Python tokenizer fallback (no native extensions required)
- ✅ FastAPI with async support
- ✅ Environment-based configuration
- ✅ Production-ready structure

## Project Structure

```
voice agent/
├── main.py              # FastAPI application entry point
├── tokenizer_patch.py   # Patches lk_blingfire import for Python 3.13
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
└── README.md           # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your LiveKit credentials:
```ini
LIVEKIT_URL=ws://your-livekit-server.com
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
```

### 3. Run the Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at `http://localhost:8000`

## How the Tokenizer Patch Works

The `tokenizer_patch.py` module intercepts the `lk_blingfire` import before LiveKit agents try to use it. Since `lk_blingfire` doesn't have a Python 3.13 wheel yet, we provide a pure-Python fallback tokenizer.

**Important**: The patch is automatically applied when `tokenizer_patch.py` is imported. In `main.py`, we import it first (before any LiveKit imports) to ensure compatibility.

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

## Development

### Running in Development Mode

Set `API_DEBUG=true` in your `.env` file to enable debug logging and auto-reload.

### Adding New Routes

1. Create route handlers in `main.py` or organize them in separate router modules
2. Include routers with `app.include_router()`

Example:
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/voice")
async def voice_endpoint():
    return {"message": "Voice agent endpoint"}

app.include_router(router)
```

## Production Deployment

1. Set `API_DEBUG=false` in production
2. Configure CORS appropriately (currently set to allow all origins)
3. Use a production ASGI server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```
4. Use a reverse proxy (nginx, Traefik) for SSL termination

## Troubleshooting

### ModuleNotFoundError: lk_blingfire

If you see this error, ensure `tokenizer_patch.py` is imported before any LiveKit imports. The patch in `main.py` should handle this automatically.

### LiveKit Connection Issues

Verify your `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` are correctly set in `.env`.

## License

MIT

