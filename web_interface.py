"""
web_interface.py

Purpose: Provides a web interface for the MyVoice project.
Serves an HTML page that connects to LiveKit rooms and displays the voice assistant interface.
"""

import logging
import os
import webbrowser
from threading import Timer

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from livekit import api
from uvicorn import run

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("myvoice.web")

app = FastAPI(title="MyVoice - Real-Time AI Voice Agent")

# Load environment variables
load_dotenv()
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")


@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve the main web interface."""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyVoice - AI Voice Assistant</title>
    <script src="https://cdn.jsdelivr.net/npm/livekit-client@latest/dist/livekit-client.umd.min.js"></script>
    <script>
        // Wait for LiveKit to be available - the correct global is LivekitClient (lowercase 'k')
        window.addEventListener('load', function() {
            console.log('Window loaded, checking LiveKit...');
            console.log('typeof LivekitClient:', typeof LivekitClient);
            console.log('typeof LiveKit:', typeof LiveKit);
            
            if (typeof LivekitClient !== 'undefined') {
                console.log('LivekitClient loaded successfully');
                console.log('LivekitClient exports:', Object.keys(LivekitClient));
            } else if (typeof LiveKit !== 'undefined') {
                console.log('LiveKit loaded successfully');
                console.log('LiveKit exports:', Object.keys(LiveKit));
            } else {
                console.error('LiveKit library failed to load');
                document.getElementById('status').textContent = 'Error: LiveKit library failed to load. Please refresh the page.';
                document.getElementById('status').className = 'status error';
            }
        });
    </script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 700px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
            font-size: 2.5em;
        }
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .status {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 500;
            font-size: 1.1em;
        }
        .status.disconnected {
            background: #fee;
            color: #c33;
        }
        .status.connected {
            background: #efe;
            color: #3c3;
        }
        .status.connecting {
            background: #ffe;
            color: #cc3;
        }
        .status.error {
            background: #fee;
            color: #c33;
        }
        button {
            width: 100%;
            padding: 18px;
            font-size: 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            margin-bottom: 15px;
        }
        button.connect {
            background: #667eea;
            color: white;
        }
        button.connect:hover:not(:disabled) {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        button.disconnect {
            background: #dc3545;
            color: white;
        }
        button.disconnect:hover:not(:disabled) {
            background: #c82333;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220, 53, 69, 0.4);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .transcript {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            min-height: 300px;
            max-height: 500px;
            overflow-y: auto;
            margin-top: 20px;
            display: none;
        }
        .message {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 8px;
            animation: fadeIn 0.3s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            background: #e3f2fd;
            text-align: right;
            margin-left: 20%;
        }
        .message.assistant {
            background: #f3e5f5;
            margin-right: 20%;
        }
        .message-label {
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 8px;
            opacity: 0.7;
        }
        .message-content {
            font-size: 16px;
            line-height: 1.5;
        }
        .mic-indicator {
            display: none;
            text-align: center;
            padding: 10px;
            color: #667eea;
            font-weight: 600;
        }
        .mic-indicator.active {
            display: block;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .info {
            background: #e7f3ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 MyVoice</h1>
        <p class="subtitle">Real-Time AI Voice Assistant</p>
        
        <div class="info">
            <strong>ℹ️ How to use:</strong> Click "Connect" to start. Grant microphone permissions when prompted. 
            Speak naturally and the AI assistant will respond with voice and text.
        </div>
        
        <div id="status" class="status disconnected">Disconnected</div>
        
        <div id="micIndicator" class="mic-indicator">🎤 Listening...</div>
        
        <button id="connectBtn" class="connect" onclick="toggleConnection()">Connect to Voice Assistant</button>
        
        <div id="transcript" class="transcript">
            <div class="message assistant">
                <div class="message-label">Assistant</div>
                <div class="message-content">Ready to chat! Click connect and start speaking.</div>
            </div>
        </div>
    </div>

    <script>
        let room = null;
        let localTrack = null;

        async function toggleConnection() {
            const btn = document.getElementById('connectBtn');
            const status = document.getElementById('status');
            const transcript = document.getElementById('transcript');
            const micIndicator = document.getElementById('micIndicator');

            if (!room || room.state === 'disconnected') {
                // Connect
                btn.disabled = true;
                btn.textContent = 'Connecting...';
                status.className = 'status connecting';
                status.textContent = 'Connecting...';

                try {
                    // Get access token from server
                    const response = await fetch('/token');
                    if (!response.ok) {
                        throw new Error('Failed to get access token');
                    }
                    const data = await response.json();
                    
                    // Check if LiveKit is loaded - the correct global is LivekitClient (lowercase 'k')
                    if (typeof LivekitClient === 'undefined') {
                        throw new Error('LiveKit client library failed to load. Please refresh the page.');
                    }
                    
                    console.log('Using LivekitClient library');
                    console.log('Available exports:', Object.keys(LivekitClient));
                    
                    // Use LivekitClient (correct case)
                    const Room = LivekitClient.Room;
                    const createLocalTracks = LivekitClient.createLocalTracks;
                    
                    if (!Room) {
                        throw new Error('Room class not found in LivekitClient');
                    }
                    if (!createLocalTracks) {
                        throw new Error('createLocalTracks function not found in LivekitClient');
                    }
                    
                    room = new Room({
                        // Enable audio capture
                        audioCaptureDefaults: {
                            source: 1, // microphone
                        }
                    });
                    
                    // Log room state changes
                    room.on('connected', () => {
                        console.log('Room connected');
                    });
                    
                    room.on('disconnected', (reason) => {
                        console.log('Room disconnected:', reason);
                    });
                    
                    // Handle audio tracks from agent
                    room.on('trackSubscribed', (track, publication, participant) => {
                        console.log('Track subscribed:', track.kind, 'from', participant.identity);
                        if (track.kind === 'audio') {
                            console.log('Setting up audio playback for agent track');
                            const audioElement = document.createElement('audio');
                            audioElement.setAttribute('playsinline', 'true');
                            audioElement.setAttribute('autoplay', 'true');
                            track.attach(audioElement);
                            document.body.appendChild(audioElement);
                            console.log('Audio element attached and added to DOM');
                        }
                    });
                    
                    // Handle local track published
                    room.on('localTrackPublished', (publication, participant) => {
                        console.log('Local track published:', publication.kind, publication.trackSid);
                    });

                    // Handle data messages (transcripts and responses)
                    room.on('dataReceived', (payload, participant, kind, topic) => {
                        console.log('Data received:', {
                            participant: participant?.identity,
                            kind: kind,
                            topic: topic,
                            payloadLength: payload.byteLength
                        });
                        
                        // Handle messages from MyVoice-agent
                        if (participant && (participant.identity === 'MyVoice-agent' || participant.identity === 'myVoice-agent')) {
                            try {
                                const text = new TextDecoder().decode(payload);
                                console.log('Decoded message:', text);
                                
                                // Determine message type based on topic
                                if (topic === 'transcription') {
                                    addMessage('user', text);
                                } else if (topic === 'assistant-response') {
                                    addMessage('assistant', text);
                                } else {
                                    // Default: treat as assistant message
                                    addMessage('assistant', text);
                                }
                            } catch (e) {
                                console.error('Error decoding message:', e);
                            }
                        } else {
                            console.log('Ignoring data from participant:', participant?.identity);
                        }
                    });

                    // Handle participant events
                    room.on('participantConnected', (participant) => {
                        console.log('Participant connected:', participant.identity);
                        if (participant.identity === 'MyVoice-agent' || participant.identity === 'myVoice-agent') {
                            status.textContent = 'Connected to AI Assistant';
                            addMessage('assistant', 'AI Assistant joined the room. You can start speaking now!');
                        }
                    });

                    room.on('participantDisconnected', (participant) => {
                        console.log('Participant disconnected:', participant.identity);
                        if (participant.identity === 'MyVoice-agent' || participant.identity === 'myVoice-agent') {
                            addMessage('assistant', 'AI Assistant left the room.');
                        }
                    });

                    // Connect to room
                    await room.connect(data.url, data.token);
                    
                    // Get user microphone
                    try {
                        console.log('Requesting microphone access...');
                        const tracks = await createLocalTracks({
                            audio: {
                                echoCancellation: true,
                                noiseSuppression: true,
                                autoGainControl: true,
                            },
                            video: false
                        });
                        
                        console.log('Microphone tracks obtained:', tracks.length);
                        
                        if (tracks.length > 0) {
                            localTrack = tracks[0];
                            console.log('Publishing local audio track to room...');
                            await room.localParticipant.publishTrack(localTrack);
                            console.log('Local audio track published successfully');
                            
                            // Log track info
                            console.log('Track info:', {
                                kind: localTrack.kind,
                                muted: localTrack.isMuted,
                                enabled: localTrack.isEnabled
                            });
                            
                            // Monitor track state
                            localTrack.on('muted', () => {
                                console.warn('Microphone muted');
                            });
                            
                            localTrack.on('unmuted', () => {
                                console.log('Microphone unmuted');
                            });
                            
                            micIndicator.classList.add('active');
                        } else {
                            throw new Error('No audio tracks obtained');
                        }
                    } catch (micError) {
                        console.error('Microphone error:', micError);
                        status.className = 'status error';
                        status.textContent = 'Microphone access denied. Please allow microphone access and try again.';
                        await room.disconnect();
                        room = null;
                        btn.disabled = false;
                        btn.textContent = 'Connect to Voice Assistant';
                        return;
                    }

                    btn.textContent = 'Disconnect';
                    btn.className = 'disconnect';
                    status.className = 'status connected';
                    status.textContent = 'Connected - Speak to the assistant!';
                    transcript.style.display = 'block';
                    
                } catch (error) {
                    console.error('Connection error:', error);
                    status.className = 'status error';
                    status.textContent = 'Connection failed: ' + error.message;
                    btn.disabled = false;
                    btn.textContent = 'Connect to Voice Assistant';
                    micIndicator.classList.remove('active');
                }
            } else {
                // Disconnect
                if (localTrack) {
                    localTrack.stop();
                    localTrack = null;
                }
                if (room) {
                    await room.disconnect();
                    room = null;
                }
                
                btn.textContent = 'Connect to Voice Assistant';
                btn.className = 'connect';
                status.className = 'status disconnected';
                status.textContent = 'Disconnected';
                transcript.style.display = 'none';
                micIndicator.classList.remove('active');
            }
            btn.disabled = false;
        }

        function addMessage(role, text) {
            const transcript = document.getElementById('transcript');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            messageDiv.innerHTML = `
                <div class="message-label">${role === 'user' ? 'You' : 'AI Assistant'}</div>
                <div class="message-content">${escapeHtml(text)}</div>
            `;
            transcript.appendChild(messageDiv);
            transcript.scrollTop = transcript.scrollHeight;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Clean up on page unload
        window.addEventListener('beforeunload', async () => {
            if (room) {
                await room.disconnect();
            }
        });
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.get("/token")
async def get_token():
    """Generate a LiveKit access token for the client."""
    if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
        raise HTTPException(
            status_code=500,
            detail="LiveKit credentials not configured. Please check your .env file."
        )

    # Create a unique room name
    room_name = "myvoice-room"  # Keep lowercase for consistency
    participant_name = "web-user"

    try:
        # Create access token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(participant_name) \
            .with_name(participant_name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            ))

        return JSONResponse({
            "token": token.to_jwt(),
            "url": LIVEKIT_URL,
            "room": room_name,
        })
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate token: {str(e)}")


def open_browser_delayed(url, delay=1.5):
    """Open browser after a delay."""
    def open_browser():
        try:
            webbrowser.open(url)
            logger.info(f"Opened browser at {url}")
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")
    
    Timer(delay, open_browser).start()


def start_server(host="127.0.0.1", port=8000, open_browser=True):
    """Start the web server and optionally open browser."""
    url = f"http://{host}:{port}"
    logger.info(f"Starting MyVoice web interface at {url}")
    
    if open_browser:
        open_browser_delayed(url)
    
    run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_server()

