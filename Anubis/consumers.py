import json
import logging
import asyncio
import threading
import time
import av
from av import VideoFrame
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
    RTCConfiguration,
)
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import CameraDetails

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
        self.lock = threading.Lock()
        self.track_id = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2  # seconds
        self.target_fps = 15  # Reduced FPS for multiple cameras
        self.delay = 1.0 / self.target_fps
        self.last_frame_time = 0
        
        logging.info(f"Initializing VideoStream with source: {source_track}")
        self._initialize_stream()

    def _initialize_stream(self):
        try:
            options = {
                'rtsp_transport': 'tcp',
                'fflags': 'nobuffer',
                'flags': 'low_delay',
                'max_delay': '500000',
                'stimeout': '5000000',
                'reorder_queue_size': '0',
                'rtsp_flags': 'prefer_tcp',
                'buffer_size': '512000',    # Reduced buffer size for multiple streams
                'thread_queue_size': '1',   # Minimal queue size
                'probesize': '500000',      # Reduced probe size
                'analyzeduration': '500000' # Reduced analysis duration
            }
            
            self.container = av.open(self.source_track, options=options)
            self.video_stream = self.container.streams.video[0]
            self.video_stream.codec_context.thread_count = 4  # Increased thread count for better performance
            
            # Reset reconnect attempts on successful connection
            self.reconnect_attempts = 0
            logging.info("Successfully opened video stream")
            
        except Exception as e:
            logging.error(f"Failed to open video stream: {str(e)}")
            if self.reconnect_attempts < self.max_reconnect_attempts:
                self.reconnect_attempts += 1
                logging.info(f"Attempting to reconnect in {self.reconnect_delay} seconds (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
                time.sleep(self.reconnect_delay)
                self._initialize_stream()
            else:
                logging.error("Max reconnection attempts reached")
                raise

    async def recv(self):
        while self.running:
            try:
                with self.lock:
                    if self.frame is not None:
                        frame = self.frame
                        self.frame = None
                        return frame
                
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logging.error(f"Error in recv: {str(e)}")
                await asyncio.sleep(0.1)

    def _update(self):
        logging.info(f"Starting video update loop for source: {self.source_track}")
        
        while self.running:
            try:
                current_time = time.time()
                
                # Skip frame if we're running too fast
                if current_time - self.last_frame_time < self.delay:
                    time.sleep(0.01)
                    continue
                
                try:
                    # Try to get a frame
                    for frame in self.container.decode(video=0):
                        if frame is None:
                            continue
                            
                        try:
                            # Convert frame to RGB24 with reduced resolution if needed
                            rgb_frame = frame.to_ndarray(format='rgb24')
                            
                            # Optional: Resize frame if needed for performance
                            # if rgb_frame.shape[1] > 1280:  # If width > 1280
                            #     rgb_frame = cv2.resize(rgb_frame, (1280, 720))
                            
                            video_frame = VideoFrame.from_ndarray(rgb_frame, format='rgb24')
                            video_frame.pts = int(current_time * 90000)
                            video_frame.time_base = 90000

                            with self.lock:
                                self.frame = video_frame
                                self.last_frame_time = current_time
                            break
                        except Exception as e:
                            logging.error(f"Error converting frame: {str(e)}")
                            continue
                            
                except Exception as e:
                    logging.error(f"Error decoding frame: {str(e)}")
                    # Attempt to reconnect if there's an error
                    if self.reconnect_attempts < self.max_reconnect_attempts:
                        self.reconnect_attempts += 1
                        logging.info(f"Attempting to reconnect in {self.reconnect_delay} seconds (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
                        time.sleep(self.reconnect_delay)
                        self._initialize_stream()
                    else:
                        logging.error("Max reconnection attempts reached")
                        break

            except Exception as e:
                logging.error(f"Error in VideoStream thread: {e}")
                time.sleep(0.1)

        logging.info(f"Video update loop ended for source: {self.source_track}")

    def start(self):
        logging.info(f"Starting VideoStream thread for source: {self.source_track}")
        self.thread = threading.Thread(target=self._update, args=())
        self.thread.daemon = False
        self.thread.start()

    def stop(self):
        logging.info(f"Stopping VideoStream for source: {self.source_track}")
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=5.0)
        if hasattr(self, 'container'):
            try:
                self.container.close()
            except Exception as e:
                logging.error(f"Error closing container: {str(e)}")
        logging.info("VideoStream stopped and resources released")


class AnubisConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.peer_connections = {}  # Store peer connections for each camera instance
        self.camera_id = None  # Store the camera ID for this consumer instance

    async def connect(self):
        # Extract camera ID from the URL path
        self.camera_id = int(self.scope['url_route']['kwargs'].get('camera_id', 0))
        if not self.camera_id:
            # If no camera_id in URL, try to extract from path
            path = self.scope['path']
            if path.startswith('/ws/stream/'):
                try:
                    self.camera_id = int(path.split('/')[-1])
                except (ValueError, IndexError):
                    await self.close()
                    return

        if not self.camera_id:
            await self.close()
            return

        # Join the camera group
        await self.channel_layer.group_add(
            f"camera_{self.camera_id}",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        try:
            # Leave the camera group
            if self.camera_id:
                await self.channel_layer.group_discard(
                    f"camera_{self.camera_id}",
                    self.channel_name
                )
            # Close all peer connections
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
                camera_id = data.get("camera_id")

                if sdp is not None and sdp_type is not None and camera_id is not None:
                    offer = RTCSessionDescription(sdp=sdp, type=sdp_type)
                    await self.handle_offer(offer, camera_id)
                else:
                    logging.error("Missing required fields in the data")
        except json.JSONDecodeError as json_error:
            logging.error(f"JSON decode error: {json_error}")
        except Exception as e:
            logging.error(f"Error in receive: {e}")

    async def handle_offer(self, offer, camera_id):
        logging.info(f"Handle offer method called for camera {camera_id}")
        try:
            if offer.sdp is None:
                logging.error("Invalid SDP data received")
                return

            # Get camera URL from database
            try:
                camera = await sync_to_async(CameraDetails.objects.get)(id=camera_id)
                camera_url = camera.url
                logging.info(f"Retrieved camera URL from database: {camera_url} for camera {camera_id}")
            except CameraDetails.DoesNotExist:
                logging.error(f"Camera {camera_id} not found in database")
                return
            except Exception as e:
                logging.error(f"Error retrieving camera URL: {str(e)}")
                return

            # Clean up existing connection if any
            if camera_id in self.peer_connections:
                old_data = self.peer_connections.pop(camera_id)
                old_data["track"].stop()
                await old_data["peer_connection"].close()
                logging.info(f"Cleaned up existing connection for camera {camera_id}")

            # Create new video stream
            try:
                track = VideoStream(camera_url)
                track.track_id = str(camera_id)
                track.start()
                logging.info(f"Created and started VideoStream for camera {camera_id}")
            except Exception as e:
                logging.error(f"Error creating VideoStream: {str(e)}")
                return

            # Create peer connection
            pc = RTCPeerConnection()
            pc.addTrack(track)
            logging.info(f"Created peer connection and added track for camera {camera_id}")

            # Store the connection
            self.peer_connections[camera_id] = {
                "peer_connection": pc,
                "track": track
            }

            # Set remote description
            await pc.setRemoteDescription(offer)
            logging.info(f"Set remote description for camera {camera_id}")

            # Create and send answer
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            logging.info(f"Created and set local description for camera {camera_id}")

            # Send answer back to client
            await self.send(text_data=json.dumps({
                "sdp": {
                    "sdp": pc.localDescription.sdp,
                    "type": pc.localDescription.type
                },
                "camera_id": camera_id
            }))
            logging.info(f"Sent answer to client for camera {camera_id}")

        except Exception as e:
            logging.error(f"Error in handle_offer for camera {camera_id}: {e}")
            import traceback
            logging.error(traceback.format_exc())
            if camera_id in self.peer_connections:
                try:
                    await self.peer_connections[camera_id]["peer_connection"].close()
                except:
                    pass
                del self.peer_connections[camera_id]

    async def stream_data(self, event):
        # Send message to WebSocket
        await self.send(text_data=event['data'])

    async def stop_stream(self, event):
        camera_id = event.get('camera_id')
        if camera_id in self.peer_connections:
            try:
                # Stop the video track
                self.peer_connections[camera_id]["track"].stop()
                # Close the peer connection
                await self.peer_connections[camera_id]["peer_connection"].close()
                # Remove from peer connections
                del self.peer_connections[camera_id]
                logging.info(f"Successfully stopped stream for camera {camera_id}")
                # Send confirmation to the client
                await self.send(text_data=json.dumps({
                    "type": "stream_stopped",
                    "camera_id": camera_id
                }))
            except Exception as e:
                logging.error(f"Error stopping stream for camera {camera_id}: {str(e)}")
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": f"Failed to stop stream for camera {camera_id}",
                    "camera_id": camera_id
                }))

    async def stop_stream_handler(self, event):
        """Handler for the stop.stream message type"""
        await self.stop_stream(event)
