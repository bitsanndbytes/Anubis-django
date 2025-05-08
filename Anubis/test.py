from imutils.video import VideoStream
import imutils
import cv2
import time
import threading

def display_camera(camera_url, stop_event, camera_name):
    vs = VideoStream(src=camera_url).start()
    time.sleep(2.0)

    while not stop_event.is_set():
        frame = vs.read()

        if frame is None:
            print(f"Error reading frame from {camera_url}")
            break

        frame = imutils.resize(frame, width=300)
        cv2.imshow(camera_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    vs.stop()

def display_multiple_cameras(camera_info_list):
    threads = []
    stop_events = [threading.Event() for _ in camera_info_list]

    for i, info in enumerate(camera_info_list):
        thread = threading.Thread(target=display_camera, args=(info['url'], stop_events[i], info['name']))
        threads.append(thread)
        thread.start()

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            for event in stop_events:
                event.set()
            break

    cv2.destroyAllWindows()

    for thread in threads:
        thread.join()

# List of dictionaries containing camera URL and name


# Call function to display multiple camera streams

