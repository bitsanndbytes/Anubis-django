from imutils.video import VideoStream
import imutils
import cv2
import time
import threading


# To pull camera streams using imutils and showing it using cv2 
def display_camera(camera_url, stop_event):
    vs = VideoStream(src=camera_url).start()
    time.sleep(2.0)



# stop event is for threads to gracefully shutdown
    while not stop_event.is_set():
        frame = vs.read()
# if camera doesnt send a frame to imutils
        if frame is None:
            print(f"Error reading frame from {camera_url}")
            break
# resize and display camera feed
        frame = imutils.resize(frame, width=1000)
        cv2.imshow(str(camera_url), frame)
#stops the streams when q button is pressed
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
#actually stops the streams
    vs.stop()


# Threads to handle streams in a dict or list
def display_multiple_cameras(camera_urls):
    threads = []
    stop_events = [threading.Event() for _ in camera_urls]

#check how many urls are in and spin up a thread for it
    for i, url in enumerate(camera_urls):
        thread = threading.Thread(target=display_camera, args=(url, stop_events[i]))
        threads.append(thread)
        thread.start()
# check if q is pressed and q the thread gracefully
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            for event in stop_events:
                event.set()
            break
# destorys all videos that cv2.imshow was displaying
    cv2.destroyAllWindows()  # Move outside the loop

#waits for all threads to finish executions
    for thread in threads:
        thread.join()


camera_urls = [
   

    # Add more camera URLs here...
]

# Call function to display multiple camera streams
display_multiple_cameras(camera_urls)