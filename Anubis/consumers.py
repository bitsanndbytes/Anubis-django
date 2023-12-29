import json
import logging
import asyncio
import threading
import cv2
import imutils
import time
from av import VideoFrame
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)
from channels.generic.websocket import AsyncWebsocketConsumer

# Set up logging
logger = logging.getLogger("aiortc")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logging.basicConfig(level=logging.INFO)


class VideoStream(VideoStreamTrack):
    kind = "video"

    def __init__(self, source_track):
        super().__init__()
        self.source_track = source_track
        self.frame = None
        self.running = True
        self.cap = cv2.VideoCapture(source_track)
        self.lock = threading.Lock()
        self.track_id = None
        self.target_fps = 35
        self.delay = 1.0 / 35

    async def recv(self):
        while self.frame is None:
            await asyncio.sleep(0.1)

        with self.lock:
            frame = self.frame
            self.frame = None

        return frame

    def start(self):
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()

    def _update(self):
        while self.running:
            try:
                ret, img = self.cap.read()
                if ret:
                    img = imutils.resize(img, width=640, height=480)
                    frame = VideoFrame.from_ndarray(img, format="bgr24")
                    frame.pts = int(time.time() * 90000)
                    frame.time_base = 90000

                    with self.lock:
                        self.frame = frame

            except Exception as e:
                logging.error(f"Error in VideoStream thread: {e}")


class AnubisConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.peer_connections = {}  # Store peer connections for each camera instance

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        try:
            for pc_data in self.peer_connections.values():
                pc = pc_data["peer_connection"]
                await pc.close()
        except Exception as e:
            logging.error(f"Error in disconnect: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if isinstance(data, dict) and "sdp" in data and isinstance(data["sdp"], dict):
                sdp = data["sdp"].get("sdp")
                sdp_type = data["sdp"].get("type")

                if sdp is not None and sdp_type is not None:
                    offer = RTCSessionDescription(sdp=sdp, type=sdp_type)
                    await self.handle_offer(offer)
                else:
                    logging.error("SDP or type field is missing or set to None in the data")
        except json.JSONDecodeError as json_error:
            logging.error(f"JSON decode error: {json_error}")
        except Exception as e:
            logging.error(f"Error in receive: {e}")

    async def handle_offer(self, offer):
        logging.info("Handle offer method called")
        try:
            if offer.sdp is None:
                logging.error("Invalid SDP data received")
                return

            camera_urls = [
                "rtsp://admin:pw@192.168.1.247:554/1",
                "rtsp://user:pw@192.168.1.78:554/stream1",
                # Add other camera URLs here
            ]

            if not camera_urls:
                logging.error("No camera URLs provided")
                return

            # Create separate VideoStreams and RTCPeerConnections for each camera URL
            for camera_id, url in enumerate(camera_urls, start=1):
                try:
                    # Create a separate VideoStream for each camera
                    track = VideoStream(url)
                    track.track_id = str(camera_id)  # Assigning an ID to the track
                    logging.info(f"Assigned ID {track.track_id} to camera {camera_id}")
                    track.start()

                    # Create separate RTCPeerConnections for each camera
                    peer_connection = RTCPeerConnection()
                    peer_connection.addTrack(track)

                    self.peer_connections[camera_id] = {
                        "peer_connection": peer_connection,
                        "track": track,
                    }

                    logging.info(f"Added track {track} to peer connection for camera {camera_id}")
                except Exception as e:
                    logging.error(f"Error creating VideoStream for camera {camera_id}: {e}")

            # Set remote description with the received offer for each camera
            for camera_id, pc_data in self.peer_connections.items():
                try:
                    await pc_data["peer_connection"].setRemoteDescription(offer)
                    answer = await pc_data["peer_connection"].createAnswer()

                    # Logging the created Answer SDP content
                    logging.info(f"Created Answer SDP for camera {camera_id}: {answer.sdp}")

                    await pc_data["peer_connection"].setLocalDescription(answer)  # Set local description after remote description

                    response = {
                        "sdp": {
                            "sdp": pc_data["peer_connection"].localDescription.sdp,
                            "type": pc_data["peer_connection"].localDescription.type,
                        },
                        "camera_id": camera_id,
                    }
                    await self.send(text_data=json.dumps(response))
                except Exception as e:
                    logging.error(f"Error handling offer for camera {camera_id}: {e}")

        except Exception as e:
            logging.error(f"Error in handle_offer: {e}")

            # Log the stack trace for debugging
            import traceback
            logging.error(traceback.format_exc())
