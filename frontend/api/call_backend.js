/**
 * Backend API Client
 * Handles all communication with the backend API
 */

// Define BackendAPI class (available globally)
var BackendAPI = class BackendAPI {
    constructor(backendUrl) {
        this.backendUrl = backendUrl.replace(/\/$/, ''); // Remove trailing slash
        this.baseUrl = `${this.backendUrl}`;
    }

    /**
     * Send text message to backend
     * @param {string} text - The text message to send
     * @returns {Promise<Object>} Response from backend
     */
    async sendText(text) {
        try {
            const response = await fetch(`${this.baseUrl}/api/voice/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    type: 'text'
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error sending text:', error);
            throw error;
        }
    }

    /**
     * Send audio to backend
     * @param {Blob} audioBlob - The audio blob to send
     * @returns {Promise<Object>} Response from backend
     */
    async sendAudio(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'audio.webm');

            const response = await fetch(`${this.baseUrl}/api/voice/chat`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error sending audio:', error);
            throw error;
        }
    }

    /**
     * Check if backend is available
     * @returns {Promise<boolean>} True if backend is available
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
            });
            return response.ok;
        } catch (error) {
            console.error('Backend health check failed:', error);
            return false;
        }
    }

    /**
     * Get backend info
     * @returns {Promise<Object>} Backend information
     */
    async getInfo() {
        try {
            const response = await fetch(`${this.baseUrl}/`, {
                method: 'GET',
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error getting backend info:', error);
            throw error;
        }
    }
};

