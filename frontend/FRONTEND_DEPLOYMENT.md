# Frontend Deployment Guide

## Quick Setup for Vercel

### 1. Deploy Frontend

```bash
cd frontend
vercel deploy
```

### 2. Configure Environment Variable

In Vercel dashboard:
1. Go to your project → Settings → Environment Variables
2. Add new variable:
   - **Name**: `VITE_BACKEND_URL`
   - **Value**: Your backend URL (e.g., `https://ai-voice-agent-backend.onrender.com`)
   - **Environment**: Select all (Production, Preview, Development)

### 3. Update Backend URL in HTML (Alternative)

If you prefer not to use environment variables, edit `index.html`:

```html
<meta name="backend-url" content="https://your-backend-url.com">
```

## File Structure

```
frontend/
├── index.html              # Main HTML page
├── main.js                 # Application logic
├── styles.css              # Styling
├── api/
│   └── call_backend.js     # Backend API client
├── vercel.json            # Vercel configuration
├── README.md              # Documentation
└── env.example.txt        # Environment variable example
```

## How Frontend Communicates with Backend

### Architecture

```
[User Browser] 
    ↓
[Frontend (Vercel)]
    ↓ HTTP/HTTPS
[Backend API (Railway/Render)]
    ↓
[Voice Agent Processing]
```

### Communication Flow

1. **User Input**:
   - User types text OR records audio
   - Frontend captures input

2. **Send Request**:
   - Frontend uses `BackendAPI` class from `api/call_backend.js`
   - Sends POST request to backend `/api/voice/chat` endpoint
   - Includes text or audio file

3. **Backend Processing**:
   - Backend receives request
   - Processes with voice agent (LiveKit, ML models, etc.)
   - Returns response

4. **Display Response**:
   - Frontend receives JSON response
   - Displays text in response section
   - Plays audio if provided

### API Endpoints Used

#### Health Check
```javascript
GET /health
```
- Used on page load to verify backend connection
- Returns: `{"status": "ok"}`

#### Chat/Message
```javascript
POST /api/voice/chat
```

**Text Request:**
```json
{
  "text": "user message",
  "type": "text"
}
```

**Audio Request:**
```
Content-Type: multipart/form-data
FormData: { audio: Blob }
```

**Response:**
```json
{
  "text": "response text",
  "message": "response message",
  "audio_url": "https://...",  // Optional
  "audio": "base64..."          // Optional
}
```

### Code Example

```javascript
// Initialize API client
const api = new BackendAPI('https://your-backend.com');

// Send text message
const response = await api.sendText('Hello, how are you?');
console.log(response.text); // Display response

// Send audio
const audioBlob = ...; // Recorded audio
const response = await api.sendAudio(audioBlob);
console.log(response.text); // Display response
```

## Deployment Size

- **HTML**: ~5 KB
- **CSS**: ~8 KB
- **JavaScript**: ~15 KB
- **Total**: ~30 KB ✅ (well under Vercel limits)

## Environment Variable Configuration

### Vercel

Add in project settings:
```
VITE_BACKEND_URL=https://your-backend.com
```

### Local Development

Create `.env.local` (not tracked in git):
```
VITE_BACKEND_URL=http://localhost:8000
```

Or update `index.html` meta tag:
```html
<meta name="backend-url" content="http://localhost:8000">
```

## Troubleshooting

### Backend Connection Issues

1. **Check CORS Settings**:
   - Backend must allow requests from Vercel domain
   - Add Vercel URL to CORS origins

2. **Verify Backend URL**:
   - Check environment variable is set correctly
   - Verify backend is running and accessible

3. **Check Browser Console**:
   - Open DevTools → Console
   - Look for network errors or CORS errors

### Audio Recording Issues

1. **HTTPS Required**:
   - Audio recording requires HTTPS (or localhost)
   - Vercel provides HTTPS automatically

2. **Microphone Permissions**:
   - Grant permissions when prompted
   - Check browser settings if blocked

3. **Browser Compatibility**:
   - Modern browsers support MediaRecorder API
   - Older browsers may not support recording

## Testing Locally

```bash
# Serve frontend locally
cd frontend
python -m http.server 8000

# Or use any static server
npx serve .

# Access at http://localhost:8000
```

Note: For audio recording, use HTTPS or localhost (browser security requirement).

## Security Considerations

1. **CORS**: Backend must configure CORS to allow frontend domain
2. **Environment Variables**: Don't expose sensitive data in client-side code
3. **HTTPS**: Always use HTTPS in production (Vercel provides this)
4. **Content Security Policy**: Consider adding CSP headers

