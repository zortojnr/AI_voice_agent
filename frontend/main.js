/**
 * Main Application Logic
 * Handles UI interactions and orchestrates backend communication
 */

// Get backend URL from environment variable or use default
// For Vercel, this should be set via environment variable VITE_BACKEND_URL
// The URL will be injected at build time or use default
const BACKEND_URL = (() => {
    // Try to get from window (injected by Vercel or build process)
    if (window.__BACKEND_URL__) {
        return window.__BACKEND_URL__;
    }
    // Try to get from meta tag (for static deployment)
    const metaTag = document.querySelector('meta[name="backend-url"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    // Default backend URL
    return 'https://ai-voice-agent-backend.onrender.com';
})();

// Initialize API client
const api = new BackendAPI(BACKEND_URL);

// DOM Elements
const textInput = document.getElementById('text-input');
const recordBtn = document.getElementById('record-btn');
const stopBtn = document.getElementById('stop-btn');
const submitBtn = document.getElementById('submit-btn');
const clearBtn = document.getElementById('clear-btn');
const recordingStatus = document.getElementById('recording-status');
const audioPreview = document.getElementById('audio-preview');
const recordedAudio = document.getElementById('recorded-audio');
const responseContainer = document.getElementById('response-container');
const audioResponse = document.getElementById('audio-response');
const responseAudio = document.getElementById('response-audio');
const statusMessage = document.getElementById('status-message');
const errorMessage = document.getElementById('error-message');
const backendUrlDisplay = document.getElementById('backend-url');

// Recording state
let mediaRecorder = null;
let audioChunks = [];
let recordedBlob = null;
let isRecording = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeUI();
    checkBrowserSupport();
    checkBackendConnection();
});

/**
 * Initialize UI elements
 */
function initializeUI() {
    // Update backend URL display
    backendUrlDisplay.textContent = BACKEND_URL;

    // Button event listeners
    submitBtn.addEventListener('click', handleSubmit);
    clearBtn.addEventListener('click', handleClear);
    recordBtn.addEventListener('click', startRecording);
    stopBtn.addEventListener('click', stopRecording);

    // Allow Enter key to submit (Ctrl+Enter for new line)
    textInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    });
}

/**
 * Check browser support for audio recording
 */
function checkBrowserSupport() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        recordBtn.disabled = false;
    } else {
        recordBtn.disabled = true;
        recordBtn.title = 'Audio recording not supported in this browser';
        console.warn('Audio recording not supported');
    }
}

/**
 * Check backend connection
 */
async function checkBackendConnection() {
    try {
        const isHealthy = await api.checkHealth();
        if (isHealthy) {
            showStatus('✓ Backend connected', 'success');
        } else {
            showError('⚠ Backend connection check failed');
        }
    } catch (error) {
        showError('⚠ Unable to reach backend: ' + error.message);
    }
}

/**
 * Start audio recording
 */
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm;codecs=opus'
        });

        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
            const audioUrl = URL.createObjectURL(recordedBlob);
            recordedAudio.src = audioUrl;
            audioPreview.classList.remove('hidden');
            
            // Stop all tracks to release microphone
            stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        isRecording = true;

        // Update UI
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        recordingStatus.classList.remove('hidden');
        textInput.disabled = true;

    } catch (error) {
        console.error('Error starting recording:', error);
        showError('Failed to start recording: ' + error.message);
    }
}

/**
 * Stop audio recording
 */
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;

        // Update UI
        recordBtn.disabled = false;
        stopBtn.disabled = true;
        recordingStatus.classList.add('hidden');
        textInput.disabled = false;
    }
}

/**
 * Handle form submission
 */
async function handleSubmit() {
    const text = textInput.value.trim();
    
    // Check if we have text or audio
    if (!text && !recordedBlob) {
        showError('Please enter text or record audio');
        return;
    }

    // Clear previous messages
    clearMessages();
    hideResponse();

    // Show loading state
    submitBtn.disabled = true;
    showStatus('Sending to backend...', 'info');

    try {
        let response;

        if (recordedBlob) {
            // Send audio
            showStatus('Sending audio to backend...', 'info');
            response = await api.sendAudio(recordedBlob);
        } else {
            // Send text
            showStatus('Sending text to backend...', 'info');
            response = await api.sendText(text);
        }

        // Display response
        displayResponse(response);

    } catch (error) {
        console.error('Error submitting:', error);
        showError('Failed to communicate with backend: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        hideStatus();
    }
}

/**
 * Display response from backend
 */
function displayResponse(response) {
    responseContainer.innerHTML = '';

    // Display text response
    if (response.text || response.message || response.response) {
        const responseText = response.text || response.message || response.response;
        const textDiv = document.createElement('div');
        textDiv.className = 'response-text';
        textDiv.textContent = responseText;
        responseContainer.appendChild(textDiv);
    }

    // Display audio response
    if (response.audio_url) {
        responseAudio.src = response.audio_url;
        audioResponse.classList.remove('hidden');
    } else if (response.audio) {
        // If audio is base64 encoded
        const audioData = `data:audio/wav;base64,${response.audio}`;
        responseAudio.src = audioData;
        audioResponse.classList.remove('hidden');
    }

    // Show response container
    responseContainer.classList.remove('hidden');
}

/**
 * Clear form and reset state
 */
function handleClear() {
    textInput.value = '';
    recordedBlob = null;
    audioChunks = [];
    audioPreview.classList.add('hidden');
    recordedAudio.src = '';
    hideResponse();
    clearMessages();
}

/**
 * Hide response section
 */
function hideResponse() {
    audioResponse.classList.add('hidden');
    responseAudio.src = '';
    responseContainer.innerHTML = '<p class="placeholder">Your response will appear here...</p>';
}

/**
 * Show status message
 */
function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.classList.remove('hidden');
    statusMessage.className = `status-message ${type}`;
}

/**
 * Hide status message
 */
function hideStatus() {
    statusMessage.classList.add('hidden');
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorMessage.classList.add('hidden');
    }, 5000);
}

/**
 * Clear all messages
 */
function clearMessages() {
    hideStatus();
    errorMessage.classList.add('hidden');
}

