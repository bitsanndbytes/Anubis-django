
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
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById("button").addEventListener('click', function() {
      document.querySelector('.bg-modal').style.display = 'flex';
  });

  document.querySelector('.close').addEventListener('click', function() {
      document.querySelector('.bg-modal').style.display = 'none';
  });
});


// Event listener for pop up camera 2
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("button2").addEventListener('click', function() {
        document.querySelector('#modal2').style.display = 'flex';
    });
  
    document.querySelector('#modal2 .close').addEventListener('click', function() {
        document.querySelector('#modal2').style.display = 'none';
    });
  });


  // Event listener for pop up camera 3
  document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("button3").addEventListener('click', function() {
        document.querySelector('#modal3').style.display = 'flex';
    });
  
    document.querySelector('#modal3 .close').addEventListener('click', function() {
        document.querySelector('#modal3').style.display = 'none';
    });
  });
  

// Event listener for pop up camera 4
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("button4").addEventListener('click', function() {
        document.querySelector('#modal4').style.display = 'flex';
    });
  
    document.querySelector('#modal4 .close').addEventListener('click', function() {
        document.querySelector('#modal4').style.display = 'none';
    });
  });





/// Test///


//test
// Function to handle WebSocket connections
// script.js

// script.js

// script.js
document.addEventListener('DOMContentLoaded', async () => {
    var pc = null;
    const serverVideo = document.querySelector("video#video1");

    // Create an empty video stream (a blank canvas)
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    const emptyStream = canvas.captureStream();

    // Set the empty stream as the serverVideo srcObject
    serverVideo.srcObject = emptyStream;
    serverVideo.addEventListener('loadedmetadata', () => {
        serverVideo.play();
    });

    let ws;

    function negotiate(cameraId) {
        return pc.createOffer().then(function (offer) {
            return pc.setLocalDescription(offer);
        }).then(function () {
            // wait for ICE gathering to complete
            return new Promise(function (resolve) {
                if (pc.iceGatheringState === 'complete') {
                    resolve();
                } else {
                    function checkState() {
                        if (pc.iceGatheringState === 'complete') {
                            pc.removeEventListener('icegatheringstatechange', checkState);
                            resolve();
                        }
                    }
                    pc.addEventListener('icegatheringstatechange', checkState);
                }
            });
        }).then(function () {
            // Modify the offer SDP to set the direction to 'recvonly'
            const modifiedOffer = new RTCSessionDescription({
                type: pc.localDescription.type,
                sdp: pc.localDescription.sdp.replace('a=sendrecv', 'a=recvonly') // Change 'sendrecv' to 'recvonly'
            });

            ws.send(JSON.stringify({
                "sdp": {
                    "sdp": modifiedOffer.sdp,
                    "type": modifiedOffer.type
                },
                "camera_id": cameraId // Specify the camera ID you want to receive here
            }));
        }).catch(function (e) {
            alert(e);
        });
    }

    function start(cameraId) {
        var config = {
            sdpSemantics: 'unified-plan',
            iceServers: [{ urls: ['stun:stun.l..com:19302'] }]
        };

        pc = new RTCPeerConnection(config);

        serverVideo.srcObject.getVideoTracks().forEach(track => {
            pc.addTrack(track);
        });
        pc.addEventListener('track', function (evt) {
            console.log("receive server video");
            if (evt.track.kind == 'video') {
                serverVideo.srcObject = evt.streams[0];
            }
        });

        document.getElementById('button').style.display = '.pulse-button';
        negotiate(cameraId);
    }

    function stop() {
        document.getElementById('stop').style.display = 'none';
        setTimeout(function () {
            pc.close();
        }, 500);
    }

    // WebSocket setup
    ws = new WebSocket('ws://127.0.0.1:8000/ws/stream/1'); // Replace 'your-server-url' with your actual server WebSocket URL

    ws.onopen = function (event) {
        console.log('WebSocket connected');
        // Call start function when WebSocket is open, specifying camera ID (in this case, 3 for the 3rd camera)
        start(1);
    };

    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.sdp && data.camera_id === 1) {
            var answer = data.sdp;
            pc.setRemoteDescription(answer).catch(function (e) {
                alert("Error setting remote description: " + e);
            });
        }
    };

    ws.onerror = function (error) {
        console.error('WebSocket error:', error);
    };

    // Call stop function on window unload to close the connection
    window.onunload = stop;
});


////////////////////////////////////////////////////////////////////////////////////
document.addEventListener('DOMContentLoaded', async () => {
    var pc = null;
    const serverVideo = document.querySelector("video#video2");

    // Create an empty video stream (a blank canvas)
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    const emptyStream = canvas.captureStream();

    // Set the empty stream as the serverVideo srcObject
    serverVideo.srcObject = emptyStream;
    serverVideo.addEventListener('loadedmetadata', () => {
        serverVideo.play();
    });

    let ws;

    function negotiate(cameraId) {
        return pc.createOffer().then(function (offer) {
            return pc.setLocalDescription(offer);
        }).then(function () {
            // wait for ICE gathering to complete
            return new Promise(function (resolve) {
                if (pc.iceGatheringState === 'complete') {
                    resolve();
                } else {
                    function checkState() {
                        if (pc.iceGatheringState === 'complete') {
                            pc.removeEventListener('icegatheringstatechange', checkState);
                            resolve();
                        }
                    }
                    pc.addEventListener('icegatheringstatechange', checkState);
                }
            });
        }).then(function () {
            // Modify the offer SDP to set the direction to 'recvonly'
            const modifiedOffer = new RTCSessionDescription({
                type: pc.localDescription.type,
                sdp: pc.localDescription.sdp.replace('a=sendrecv', 'a=recvonly') // Change 'sendrecv' to 'recvonly'
            });

            ws.send(JSON.stringify({
                "sdp": {
                    "sdp": modifiedOffer.sdp,
                    "type": modifiedOffer.type
                },
                "camera_id": cameraId // Specify the camera ID you want to receive here
            }));
        }).catch(function (e) {
            alert(e);
        });
    }

    function start(cameraId) {
        var config = {
            sdpSemantics: 'unified-plan',
            iceServers: [{ urls: ['stun:stun.l..com:19302'] }]
        };

        pc = new RTCPeerConnection(config);

        serverVideo.srcObject.getVideoTracks().forEach(track => {
            pc.addTrack(track);
        });
        pc.addEventListener('track', function (evt) {
            console.log("receive server video");
            if (evt.track.kind == 'video') {
                serverVideo.srcObject = evt.streams[0];
            }
        });

        document.getElementById('button').style.display = '.pulse-button';
        negotiate(cameraId);
    }

    function stop() {
        document.getElementById('stop').style.display = 'none';
        setTimeout(function () {
            pc.close();
        }, 500);
    }

    // WebSocket setup
    ws = new WebSocket('ws://127.0.0.1:8000/ws/stream/2'); // Replace 'your-server-url' with your actual server WebSocket URL

    ws.onopen = function (event) {
        console.log('WebSocket connected');
        // Call start function when WebSocket is open, specifying camera ID (in this case, 3 for the 3rd camera)
        start(2);
    };

    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.sdp && data.camera_id === 2) {
            var answer = data.sdp;
            pc.setRemoteDescription(answer).catch(function (e) {
                alert("Error setting remote description: " + e);
            });
        }
    };

    ws.onerror = function (error) {
        console.error('WebSocket error:', error);
    };

    // Call stop function on window unload to close the connection
    window.onunload = stop;
});


////// Camera 3 //////////////
document.addEventListener('DOMContentLoaded', async () => {
    var pc = null;
    const serverVideo = document.querySelector("video#video3");

    // Create an empty video stream (a blank canvas)
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    const emptyStream = canvas.captureStream();

    // Set the empty stream as the serverVideo srcObject
    serverVideo.srcObject = emptyStream;
    serverVideo.addEventListener('loadedmetadata', () => {
        serverVideo.play();
    });

    let ws;

    function negotiate(cameraId) {
        return pc.createOffer().then(function (offer) {
            return pc.setLocalDescription(offer);
        }).then(function () {
            // wait for ICE gathering to complete
            return new Promise(function (resolve) {
                if (pc.iceGatheringState === 'complete') {
                    resolve();
                } else {
                    function checkState() {
                        if (pc.iceGatheringState === 'complete') {
                            pc.removeEventListener('icegatheringstatechange', checkState);
                            resolve();
                        }
                    }
                    pc.addEventListener('icegatheringstatechange', checkState);
                }
            });
        }).then(function () {
            // Modify the offer SDP to set the direction to 'recvonly'
            const modifiedOffer = new RTCSessionDescription({
                type: pc.localDescription.type,
                sdp: pc.localDescription.sdp.replace('a=sendrecv', 'a=recvonly') // Change 'sendrecv' to 'recvonly'
            });

            ws.send(JSON.stringify({
                "sdp": {
                    "sdp": modifiedOffer.sdp,
                    "type": modifiedOffer.type
                },
                "camera_id": cameraId // Specify the camera ID you want to receive here
            }));
        }).catch(function (e) {
            alert(e);
        });
    }

    function start(cameraId) {
        var config = {
            sdpSemantics: 'unified-plan',
            iceServers: [{ urls: ['stun:stun.l..com:19302'] }]
        };

        pc = new RTCPeerConnection(config);

        serverVideo.srcObject.getVideoTracks().forEach(track => {
            pc.addTrack(track);
        });
        pc.addEventListener('track', function (evt) {
            console.log("receive server video");
            if (evt.track.kind == 'video') {
                serverVideo.srcObject = evt.streams[0];
            }
        });

        document.getElementById('button').style.display = '.pulse-button';
        negotiate(cameraId);
    }

    function stop() {
        document.getElementById('stop').style.display = 'none';
        setTimeout(function () {
            pc.close();
        }, 500);
    }

    // WebSocket setup
    ws = new WebSocket('ws://127.0.0.1:8000/ws/stream/3'); // Replace 'your-server-url' with your actual server WebSocket URL

    ws.onopen = function (event) {
        console.log('WebSocket connected');
        // Call start function when WebSocket is open, specifying camera ID (in this case, 3 for the 3rd camera)
        start(3);
    };

    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.sdp && data.camera_id === 3) {
            var answer = data.sdp;
            pc.setRemoteDescription(answer).catch(function (e) {
                alert("Error setting remote description: " + e);
            });
        }
    };

    ws.onerror = function (error) {
        console.error('WebSocket error:', error);
    };

    // Call stop function on window unload to close the connection
    window.onunload = stop;
});

////// camera4  ////////////////////////////////////////

