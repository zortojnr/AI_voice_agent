# Frontend Setup Summary

## Complete File Tree

```
frontend/
├── index.html                  # Main HTML page
├── main.js                     # Application logic
├── styles.css                  # Styling (dark theme)
├── package.json                # Package configuration for Vercel
├── vercel.json                 # Vercel deployment configuration
├── env.example.txt             # Environment variable example
├── README.md                   # Frontend documentation
├── FRONTEND_DEPLOYMENT.md      # Deployment guide
└── api/
    └── call_backend.js         # Backend API client
```

## Final `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        }
      ]
    }
  ]
}
```

## How Frontend Communicates with Backend

### Architecture Flow

```
[User Browser]
    ↓
[Frontend (Vercel)]
    ↓ HTTP/HTTPS Request
[Backend API (Railway/Render)]
    ↓
[Voice Agent Processing]
    ↓
[Response (JSON + optional audio)]
    ↓
[Frontend displays/plays response]
```

### Communication Details

1. **Backend URL Configuration**:
   - Frontend reads backend URL from:
     - Meta tag in `index.html`: `<meta name="backend-url" content="...">`
     - Or defaults to: `https://ai-voice-agent-backend.onrender.com`
   - For Vercel, you can also set environment variable `VITE_BACKEND_URL` (though current implementation uses meta tag)

2. **API Client (`api/call_backend.js`)**:
   - Defines `BackendAPI` class
   - Handles all HTTP communication
   - Methods:
     - `sendText(text)` - POST text to `/api/voice/chat`
     - `sendAudio(audioBlob)` - POST audio file to `/api/voice/chat`
     - `checkHealth()` - GET `/health` endpoint
     - `getInfo()` - GET `/` endpoint

3. **Main Application (`main.js`)**:
   - Initializes `BackendAPI` with backend URL
   - Handles UI interactions (text input, audio recording)
   - Sends requests via `BackendAPI`
   - Displays responses (text + audio playback)

4. **Request Format**:
   - **Text Request**: 
     ```json
     POST /api/voice/chat
     Content-Type: application/json
     {
       "text": "user message",
       "type": "text"
     }
     ```
   
   - **Audio Request**:
     ```
     POST /api/voice/chat
     Content-Type: multipart/form-data
     FormData: { audio: Blob (WebM format) }
     ```

5. **Response Format**:
   ```json
   {
     "text": "response text",
     "message": "response message",
     "audio_url": "https://...",  // Optional audio URL
     "audio": "base64..."          // Optional base64 audio
   }
   ```

6. **CORS Configuration**:
   - Frontend configured to allow CORS (via Vercel headers)
   - Backend must allow requests from Vercel domain
   - Add Vercel URL to backend's CORS origins

### Example Communication Flow

```javascript
// 1. User types "Hello" and clicks Send
textInput.value = "Hello";
submitBtn.click();

// 2. Frontend calls API
const response = await api.sendText("Hello");

// 3. Backend receives at POST /api/voice/chat
// Processes with voice agent
// Returns: { text: "Hello! How can I help you?" }

// 4. Frontend displays response
responseContainer.textContent = response.text;
```

## Deployment Size

- **Total Size**: ~30-50 KB (HTML + CSS + JS)
- **Well Under 250 MB Limit**: ✅
- **No Build Step Required**: Pure static files
- **Fast Loading**: Optimized for performance

## Environment Variable Setup

### Option 1: Update HTML Meta Tag (Recommended)

Edit `frontend/index.html`:
```html
<meta name="backend-url" content="https://your-backend-url.com">
```

### Option 2: Vercel Environment Variable

1. Go to Vercel dashboard → Project → Settings → Environment Variables
2. Add variable:
   - Name: `VITE_BACKEND_URL`
   - Value: `https://your-backend-url.com`
   - Environment: All (Production, Preview, Development)

Note: Current implementation reads from meta tag first, but you can modify `main.js` to also check environment variables.

## Ready for Deployment

The frontend is now ready for `vercel deploy`:

```bash
cd frontend
vercel deploy
```

Or deploy with production:
```bash
vercel --prod
```

## Features Implemented

- ✅ Clean, modern UI with dark theme
- ✅ Text input with Enter key support
- ✅ Audio recording (browser-based WebM)
- ✅ Real-time backend communication
- ✅ Text response display
- ✅ Audio response playback
- ✅ Error handling and status messages
- ✅ Responsive design
- ✅ Health check on page load
- ✅ Backend URL display in footer

## Backend Requirements

The backend must expose these endpoints:

1. **Health Check**: `GET /health` → `{"status": "ok"}`
2. **Chat**: `POST /api/voice/chat` → Accepts text or audio, returns JSON

See `FRONTEND_DEPLOYMENT.md` for detailed API specifications.

