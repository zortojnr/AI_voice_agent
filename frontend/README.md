# AI Voice Agent Frontend

Lightweight frontend for the AI Voice Agent project, optimized for Vercel deployment.

## Features

- ✅ Clean, modern UI with dark theme
- ✅ Text input for messages
- ✅ Audio recording support (browser-based)
- ✅ Real-time communication with backend API
- ✅ Audio playback for responses
- ✅ Environment variable configuration
- ✅ Responsive design

## Project Structure

```
frontend/
├── index.html          # Main HTML page
├── main.js             # Application logic
├── styles.css          # Styling
├── api/
│   └── call_backend.js # Backend API client
├── vercel.json         # Vercel configuration
└── README.md          # This file
```

## Setup

### 1. Configure Backend URL

In Vercel dashboard:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add a new variable:
   - **Name**: `VITE_BACKEND_URL`
   - **Value**: `https://ai-voice-agent-backend.onrender.com` (or your backend URL)
   - **Environment**: Production, Preview, Development (select all)

### 2. Deploy to Vercel

```bash
# Install Vercel CLI if needed
npm i -g vercel

# Deploy
cd frontend
vercel deploy

# Or deploy with production
vercel --prod
```

## Environment Variables

The frontend uses `VITE_BACKEND_URL` environment variable:

- **Vercel**: Add in project settings → Environment Variables
- **Local Development**: Create a `.env.local` file (not tracked in git)

Example `.env.local`:
```
VITE_BACKEND_URL=https://ai-voice-agent-backend.onrender.com
```

## Backend API Endpoints

The frontend expects the following backend endpoints:

### Health Check
```
GET /health
```
Returns: `{"status": "ok"}`

### Chat/Message
```
POST /api/voice/chat
Content-Type: application/json
Body: {
  "text": "user message",
  "type": "text"
}
```

Or with audio:
```
POST /api/voice/chat
Content-Type: multipart/form-data
Body: FormData with "audio" file
```

Response:
```json
{
  "text": "response text",
  "message": "response message",
  "audio_url": "https://...",  // Optional
  "audio": "base64..."          // Optional
}
```

## Features

### Text Input
- Users can type messages in the textarea
- Press Enter to submit (Ctrl+Enter for new line)
- Or click "Send Message" button

### Audio Recording
- Click "Record Audio" to start recording
- Browser will request microphone permission
- Click "Stop Recording" when done
- Preview recorded audio before sending
- Audio is sent as WebM format

### Response Display
- Text responses appear in the response section
- Audio responses are played back automatically
- Status messages show connection and progress

## Browser Support

- ✅ Modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ Audio recording requires HTTPS (or localhost)
- ⚠️ Audio recording may not work in older browsers

## Deployment Size

- **Total size**: ~50 KB (HTML + CSS + JS)
- **Well under Vercel limits**: ✅
- **No dependencies**: Pure vanilla JavaScript
- **Fast loading**: Optimized for performance

## Local Development

```bash
# Serve locally (requires a simple HTTP server)
python -m http.server 8000

# Or use Vite for development
npm install -g vite
vite
```

Note: For audio recording, you'll need HTTPS or localhost (browser security requirement).

## Troubleshooting

### Backend Connection Failed
- Check `VITE_BACKEND_URL` is set correctly in Vercel
- Verify backend is running and accessible
- Check CORS settings on backend

### Audio Recording Not Working
- Ensure you're on HTTPS or localhost
- Grant microphone permissions when prompted
- Check browser console for errors

### Environment Variable Not Working
- Ensure variable name is `VITE_BACKEND_URL` (with VITE_ prefix)
- Redeploy after adding environment variables
- Check Vercel logs for errors

## API Client Usage

The `BackendAPI` class in `api/call_backend.js` handles all backend communication:

```javascript
import BackendAPI from './api/call_backend.js';

const api = new BackendAPI('https://your-backend.com');

// Send text
const response = await api.sendText('Hello');

// Send audio
const audioBlob = ...; // Your audio blob
const response = await api.sendAudio(audioBlob);

// Check health
const isHealthy = await api.checkHealth();
```

