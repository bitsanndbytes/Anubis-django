import cv2
import time
import threading

def display_camera(camera_url, stop_event):
    cap = cv2.VideoCapture(camera_url)

    if not cap.isOpened():
        print(f"Error opening video stream from {camera_url}")
        return

    while not stop_event.is_set():
        ret, frame = cap.read()

        if not ret:
            print(f"Error reading frame from {camera_url}")
            break

        frame = cv2.resize(frame, (700, int(frame.shape[0] * (700 / frame.shape[1]))))
        cv2.imshow(str(camera_url), frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()

def display_multiple_cameras(camera_urls):
    threads = []
    stop_events = [threading.Event() for _ in camera_urls]

    for i, url in enumerate(camera_urls):
        thread = threading.Thread(target=display_camera, args=(url, stop_events[i]))
        threads.append(thread)
        thread.start()

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            for event in stop_events:
                event.set()
            break

    cv2.destroyAllWindows()  # Move outside the loop

    for thread in threads:
        thread.join()

# Example list of camera URLs
camera_urls = [
    

    # Add more camera URLs here...
]

# Call function to display multiple camera streams
display_multiple_cameras(camera_urls)
