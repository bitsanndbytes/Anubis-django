var serverIp = "{{ server_ip }}";

// Makes dashboard screen menu always collapses
document.addEventListener("DOMContentLoaded", function() {
    const checkbox = document.getElementById("checkbox");

    // Initially collapse the checkbox
    checkbox.checked = true;
   
    // Event listener for label (hamburger icon) click
    document.querySelector('.label').addEventListener("click", function(event) {
        checkbox.checked = !checkbox.checked;
        event.preventDefault(); // Prevents the default checkbox behavior also helps the button from not sticking
    });
});

// Event listener to pop up form for camera1
document.getElementById("button").addEventListener('click', function() {
    document.querySelector('.bg-modal').style.display = 'flex';
    document.querySelector('.pulse-button').style.display = 'none';
});

document.querySelector('.close').addEventListener('click', function() {
    document.querySelector('.bg-modal').style.display = 'none';
    document.querySelector('.pulse-button').style.display = 'flex';
});

// Add trash button functionality for camera 1
document.getElementById("trash1").addEventListener('click', function() {
    if (confirm('Are you sure you want to remove this camera?')) {
        const cameraId = 1;
        // Stop the stream on the frontend
        if (handlers[cameraId]) {
            handlers[cameraId].stop();
            delete handlers[cameraId];
        }
        // Clear the video element
        const video = document.getElementById('video1');
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
        video.srcObject = null;
        video.load();
        // Show the add button again
        document.querySelectorAll('.pulse-button')[cameraId - 1].style.display = 'flex';
        // Send request to backend to stop the stream
        fetch(`/stop_stream/${cameraId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).catch(error => console.error('Error stopping stream:', error));
    }
});

// Event listener for pop up camera 2
document.getElementById("button2").addEventListener('click', function() {
    document.querySelector('#modal2').style.display = 'flex';
    document.querySelectorAll('.pulse-button')[1].style.display = 'none';
});

document.querySelector('#modal2 .close').addEventListener('click', function() {
    document.querySelector('#modal2').style.display = 'none';
    document.querySelectorAll('.pulse-button')[1].style.display = 'flex';
});

// Add trash button functionality for camera 2
document.getElementById("trash2").addEventListener('click', function() {
    if (confirm('Are you sure you want to remove this camera?')) {
        const cameraId = 2;
        // Stop the stream on the frontend
        if (handlers[cameraId]) {
            handlers[cameraId].stop();
            delete handlers[cameraId];
        }
        // Clear the video element
        const video = document.getElementById('video2');
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
        video.srcObject = null;
        video.load();
        // Show the add button again
        document.querySelectorAll('.pulse-button')[cameraId - 1].style.display = 'flex';
        // Send request to backend to stop the stream
        fetch(`/stop_stream/${cameraId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).catch(error => console.error('Error stopping stream:', error));
    }
});

// Event listener for pop up camera 3
document.getElementById("button3").addEventListener('click', function() {
    document.querySelector('#modal3').style.display = 'flex';
    document.querySelectorAll('.pulse-button')[2].style.display = 'none';
});

document.querySelector('#modal3 .close').addEventListener('click', function() {
    document.querySelector('#modal3').style.display = 'none';
    document.querySelectorAll('.pulse-button')[2].style.display = 'flex';
});

// Add trash button functionality for camera 3
document.getElementById("trash3").addEventListener('click', function() {
    if (confirm('Are you sure you want to remove this camera?')) {
        const cameraId = 3;
        // Stop the stream on the frontend
        if (handlers[cameraId]) {
            handlers[cameraId].stop();
            delete handlers[cameraId];
        }
        // Clear the video element
        const video = document.getElementById('video3');
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
        video.srcObject = null;
        video.load();
        // Show the add button again
        document.querySelectorAll('.pulse-button')[cameraId - 1].style.display = 'flex';
        // Send request to backend to stop the stream
        fetch(`/stop_stream/${cameraId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).catch(error => console.error('Error stopping stream:', error));
    }
});

// Event listener for pop up camera 4
document.getElementById("button4").addEventListener('click', function() {
    document.querySelector('#modal4').style.display = 'flex';
    document.querySelectorAll('.pulse-button')[3].style.display = 'none';
});

document.querySelector('#modal4 .close').addEventListener('click', function() {
    document.querySelector('#modal4').style.display = 'none';
    document.querySelectorAll('.pulse-button')[3].style.display = 'flex';
});

// Add trash button functionality for camera 4
document.getElementById("trash4").addEventListener('click', function() {
    if (confirm('Are you sure you want to remove this camera?')) {
        const cameraId = 4;
        // Stop the stream on the frontend
        if (handlers[cameraId]) {
            handlers[cameraId].stop();
            delete handlers[cameraId];
        }
        // Clear the video element
        const video = document.getElementById('video4');
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
        video.srcObject = null;
        video.load();
        // Show the add button again
        document.querySelectorAll('.pulse-button')[cameraId - 1].style.display = 'flex';
        // Send request to backend to stop the stream
        fetch(`/stop_stream/${cameraId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).catch(error => console.error('Error stopping stream:', error));
    }
});

// Global configuration and handlers
const CONFIG = {
    MAX_RETRIES: 3,
    RETRY_DELAY: 5000, // 5 seconds
    CONNECTION_TIMEOUT: 10000, // 10 seconds
    SERVER_URL: `ws://${window.location.hostname}:${window.location.port}/ws/stream/`
};

// Global handlers object to store WebSocket handlers
const handlers = {};

// Enhanced logging function
function log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${type.toUpperCase()}] ${message}`;
    console.log(logMessage);
}

// Connection status indicators
function updateConnectionStatus(videoId, status, message) {
    const statusElement = document.getElementById(`status-${videoId}`);
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.className = `status-indicator ${status}`;
    }
    log(`Camera ${videoId}: ${message}`, status);
}

// WebSocket connection handler
class WebSocketHandler {
    constructor(videoId) {
        this.videoId = videoId;
        this.retryCount = 0;
        this.connectionTimeout = null;
        this.ws = null;
        this.pc = null;
        this.serverVideo = document.querySelector(`#video${videoId}`);
        this.isConnecting = false;
        this.retryTimer = null;
        this.intentionallyStopped = false;  // New flag to track intentional stops
        log(`Initialized WebSocketHandler for camera ${videoId}`);

        // Ensure video element is properly configured
        if (this.serverVideo) {
            this.serverVideo.autoplay = true;
            this.serverVideo.playsInline = true;
            this.serverVideo.muted = true; // Required for autoplay
            this.serverVideo.style.width = '100%';
            this.serverVideo.style.height = '100%';
            this.serverVideo.style.objectFit = 'cover';
            log(`Configured video element for camera ${videoId}`);
        } else {
            log(`Video element not found for camera ${videoId}`, 'error');
        }
    }

    initializeEmptyStream() {
        log(`Initializing empty stream for camera ${this.videoId}`);
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        const emptyStream = canvas.captureStream();
        this.serverVideo.srcObject = emptyStream;
        this.serverVideo.addEventListener('loadedmetadata', () => {
            this.serverVideo.play();
            log(`Empty stream playing for camera ${this.videoId}`);
        });
    }

    async negotiate(cameraId) {
        if (!this.pc || this.pc.connectionState === 'closed') {
            log(`PeerConnection not available for camera ${cameraId}`, 'error');
            return;
        }

        try {
            log(`Creating offer for camera ${cameraId}`);
            const offer = await this.pc.createOffer({
                offerToReceiveVideo: true,
                offerToReceiveAudio: false
            });
            log(`Offer created for camera ${cameraId}: ${offer.type}`);

            await this.pc.setLocalDescription(offer);
            log(`Local description set for camera ${cameraId}`);

            // Wait for ICE gathering to complete
            if (this.pc.iceGatheringState !== 'complete') {
                log(`Waiting for ICE gathering to complete for camera ${cameraId}`);
                await new Promise((resolve) => {
                    const checkState = () => {
                        if (this.pc.iceGatheringState === 'complete') {
                            this.pc.removeEventListener('icegatheringstatechange', checkState);
                            log(`ICE gathering complete for camera ${cameraId}`);
                            resolve();
                        }
                    };
                    this.pc.addEventListener('icegatheringstatechange', checkState);
                });
            }

            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                const message = {
                    sdp: {
                        sdp: this.pc.localDescription.sdp,
                        type: this.pc.localDescription.type
                    },
                    camera_id: cameraId
                };
                log(`Sending offer to server: ${JSON.stringify(message)}`);
                this.ws.send(JSON.stringify(message));
                log(`Sent offer to server for camera ${cameraId}`);
            } else {
                throw new Error('WebSocket is not open');
            }
        } catch (error) {
            log(`Error in negotiate for camera ${cameraId}: ${error.message}`, 'error');
            updateConnectionStatus(this.videoId, 'error', 'Connection failed');
            this.retryConnection();
        }
    }

    start(cameraId) {
        log(`Starting WebRTC connection for camera ${cameraId}`);
        if (this.pc) {
            this.pc.close();
            log(`Closed existing PeerConnection for camera ${cameraId}`);
        }

        const config = {
            sdpSemantics: 'unified-plan',
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' },
                { urls: 'stun:stun2.l.google.com:19302' }
            ]
        };

        this.pc = new RTCPeerConnection(config);
        log(`Created new PeerConnection for camera ${cameraId}`);

        // Add event listeners for ICE candidates
        this.pc.onicecandidate = (event) => {
            if (event.candidate) {
                log(`New ICE candidate for camera ${cameraId}: ${event.candidate.candidate}`);
            } else {
                log(`ICE gathering complete for camera ${cameraId}`);
            }
        };

        this.pc.addEventListener('track', (evt) => {
            log(`Received track for camera ${cameraId}: ${evt.track.kind}`);
            if (evt.track.kind === 'video') {
                try {
                    // Clear any existing stream
                    if (this.serverVideo.srcObject) {
                        this.serverVideo.srcObject.getTracks().forEach(track => track.stop());
                    }
                    
                    // Set the new stream
                    this.serverVideo.srcObject = evt.streams[0];
                    log(`Set video source for camera ${cameraId}`);

                    // Ensure video plays
                    this.serverVideo.onloadedmetadata = () => {
                        log(`Video metadata loaded for camera ${cameraId}`);
                        this.serverVideo.play().catch(error => {
                            log(`Error playing video for camera ${cameraId}: ${error.message}`, 'error');
                        });
                    };

                    updateConnectionStatus(this.videoId, 'connected', 'Connected');
                    this.retryCount = 0;
                } catch (error) {
                    log(`Error setting video stream for camera ${cameraId}: ${error.message}`, 'error');
                }
            }
        });

        this.pc.oniceconnectionstatechange = () => {
            log(`ICE connection state changed for camera ${cameraId}: ${this.pc.iceConnectionState}`);
            if (this.pc.iceConnectionState === 'failed') {
                log(`ICE connection failed for camera ${cameraId}`, 'error');
                updateConnectionStatus(this.videoId, 'error', 'Connection failed');
                this.retryConnection();
            }
        };

        this.pc.onconnectionstatechange = () => {
            log(`Connection state changed for camera ${cameraId}: ${this.pc.connectionState}`);
            if (this.pc.connectionState === 'failed') {
                log(`Connection failed for camera ${cameraId}`, 'error');
                updateConnectionStatus(this.videoId, 'error', 'Connection failed');
                this.retryConnection();
            }
        };

        this.negotiate(cameraId);
    }

    connect() {
        if (this.intentionallyStopped) {
            log(`Not connecting camera ${this.videoId} as it was intentionally stopped`);
            return;
        }

        if (this.isConnecting) {
            log(`Already connecting for camera ${this.videoId}`, 'warn');
            return;
        }
        this.isConnecting = true;

        log(`Connecting WebSocket for camera ${this.videoId}`);
        updateConnectionStatus(this.videoId, 'connecting', 'Connecting...');
        
        if (this.ws) {
            this.ws.close();
            log(`Closed existing WebSocket for camera ${this.videoId}`);
        }

        const wsUrl = `${CONFIG.SERVER_URL}${this.videoId}`;
        this.ws = new WebSocket(wsUrl);
        log(`Created new WebSocket for camera ${this.videoId}: ${wsUrl}`);
        
        this.connectionTimeout = setTimeout(() => {
            if (this.ws.readyState !== WebSocket.OPEN) {
                log(`Connection timeout for camera ${this.videoId}`, 'error');
                this.ws.close();
                updateConnectionStatus(this.videoId, 'error', 'Connection timeout');
                this.isConnecting = false;
                this.retryConnection();
            }
        }, CONFIG.CONNECTION_TIMEOUT);

        this.ws.onopen = () => {
            log(`WebSocket opened for camera ${this.videoId}`);
            clearTimeout(this.connectionTimeout);
            this.start(this.videoId);
            this.isConnecting = false;
        };

        this.ws.onmessage = async (event) => {
            try {
                const data = JSON.parse(event.data);
                log(`Received message for camera ${this.videoId}: ${JSON.stringify(data)}`);
                
                if (data.sdp && data.camera_id === this.videoId) {
                    log(`Processing SDP answer for camera ${this.videoId}`);
                    try {
                        await this.pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
                        log(`Remote description set for camera ${this.videoId}`);
                        updateConnectionStatus(this.videoId, 'connected', 'Connected');
                    } catch (error) {
                        log(`Error setting remote description for camera ${this.videoId}: ${error.message}`, 'error');
                        updateConnectionStatus(this.videoId, 'error', 'Stream error');
                    }
                } else if (data.type === 'stream_stopped' && data.camera_id === this.videoId) {
                    log(`Stream stopped confirmation received for camera ${this.videoId}`);
                    this.stop();
                    // Show the add button again
                    document.querySelectorAll('.pulse-button')[this.videoId - 1].style.display = 'flex';
                } else if (data.type === 'error' && data.camera_id === this.videoId) {
                    log(`Error from server for camera ${this.videoId}: ${data.message}`, 'error');
                    updateConnectionStatus(this.videoId, 'error', data.message);
                }
            } catch (error) {
                log(`Error processing message for camera ${this.videoId}: ${error.message}`, 'error');
            }
        };

        this.ws.onerror = (error) => {
            log(`WebSocket error for camera ${this.videoId}: ${error.message}`, 'error');
            updateConnectionStatus(this.videoId, 'error', 'Connection error');
            this.isConnecting = false;
        };

        this.ws.onclose = () => {
            log(`WebSocket closed for camera ${this.videoId}`);
            clearTimeout(this.connectionTimeout);
            this.isConnecting = false;
            
            // Only attempt to reconnect if not intentionally stopped
            if (!this.intentionallyStopped && this.retryCount < CONFIG.MAX_RETRIES) {
                this.retryConnection();
            } else if (this.intentionallyStopped) {
                log(`WebSocket closed intentionally for camera ${this.videoId}`);
                updateConnectionStatus(this.videoId, 'disconnected', 'Disconnected');
            } else {
                updateConnectionStatus(this.videoId, 'error', 'Max retries reached');
            }
        };
    }

    retryConnection() {
        if (this.intentionallyStopped) {
            log(`Not retrying connection for camera ${this.videoId} as it was intentionally stopped`);
            return;
        }

        if (this.retryTimer) {
            clearTimeout(this.retryTimer);
        }

        this.retryCount++;
        if (this.retryCount <= CONFIG.MAX_RETRIES) {
            const delay = CONFIG.RETRY_DELAY * Math.pow(1.5, this.retryCount - 1);
            log(`Retrying connection for camera ${this.videoId} in ${delay/1000} seconds (attempt ${this.retryCount}/${CONFIG.MAX_RETRIES})`);
            updateConnectionStatus(this.videoId, 'connecting', `Retrying (${this.retryCount}/${CONFIG.MAX_RETRIES})...`);
            this.retryTimer = setTimeout(() => this.connect(), delay);
        } else {
            log(`Max retries reached for camera ${this.videoId}`, 'error');
            updateConnectionStatus(this.videoId, 'error', 'Max retries reached');
        }
    }

    stop() {
        log(`Stopping connection for camera ${this.videoId}`);
        this.intentionallyStopped = true;  // Set the flag when intentionally stopping
        if (this.retryTimer) {
            clearTimeout(this.retryTimer);
        }
        if (this.connectionTimeout) {
            clearTimeout(this.connectionTimeout);
        }
        if (this.ws) {
            this.ws.close();
        }
        if (this.pc) {
            this.pc.close();
        }
        this.isConnecting = false;
        updateConnectionStatus(this.videoId, 'disconnected', 'Disconnected');
    }
}

// Initialize only when needed
document.addEventListener('DOMContentLoaded', () => {
    // Create status indicators for each video
    for (let i = 1; i <= 4; i++) {
        const statusDiv = document.createElement('div');
        statusDiv.id = `status-${i}`;
        statusDiv.className = 'status-indicator';
        document.querySelector(`#video${i}`).parentNode.appendChild(statusDiv);
    }

    // Add event listeners for the add buttons
    document.querySelectorAll('.btn').forEach((button, index) => {
        button.addEventListener('click', async () => {
            const cameraId = index + 1;
            const cameraName = document.getElementById(`username${cameraId === 1 ? '' : cameraId}`).value;
            const rtspUrl = document.getElementById(`nm${cameraId === 1 ? '' : cameraId}`).value;

            if (cameraName && rtspUrl) {
                try {
                    // First, save camera details to the server
                    const response = await fetch('/save_camera/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            camera_id: cameraId,
                            camera_name: cameraName,
                            rtsp_url: rtspUrl
                        })
                    });

                    if (!response.ok) {
                        throw new Error('Failed to save camera details');
                    }

                    // Create handler and connect
                    if (!handlers[cameraId]) {
                        handlers[cameraId] = new WebSocketHandler(cameraId);
                    }
                    handlers[cameraId].connect();

                    // Close the modal and show pulse button - using the same selectors as video1
                    const modal = cameraId === 1 ? '.bg-modal' : `#modal${cameraId}`;
                    const pulseButtonIndex = cameraId - 1;
                    
                    document.querySelector(modal).style.display = 'none';
                    document.querySelectorAll('.pulse-button')[pulseButtonIndex].style.display = 'flex';

                } catch (error) {
                    console.error('Error adding camera:', error);
                    updateConnectionStatus(cameraId, 'error', 'Failed to add camera');
                }
            }
        });
    });

    // Clean up on page unload
    window.onunload = () => {
        Object.values(handlers).forEach(handler => handler.stop());
    };
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

