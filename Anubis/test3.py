from vidgear.gears import CamGear
import cv2
import imutils
import threading

# RTSP stream URLs for three cameras
rtsp_stream_urls = [
    "rtsp://hackergod:water44@192.168.1.78:554/stream1",
    "rtsp://192.168.1.246:554/stream0",
    # Add your other stream URLs here
]

# Create a list to hold CamGear objects for each stream
streams = []

# Function to read frames from a stream
def read_frames(stream):
    while True:
        frame = stream.read()
        if frame is None:
            break
        frame = imutils.resize(frame, width=600)
        cv2.imshow(stream.stream_source, frame)

    stream.stop()

# Open the RTSP streams for each camera and start a separate thread for each stream
for url in rtsp_stream_urls:
    stream = CamGear(source=url).start()
    streams.append(stream)
    thread = threading.Thread(target=read_frames, args=(stream,))
    thread.daemon = True
    thread.start()

# Wait for 'q' to be pressed to stop
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# Clean up
cv2.destroyAllWindows()
