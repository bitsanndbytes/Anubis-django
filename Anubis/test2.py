from facenet_pytorch import MTCNN
import torch
import cv2
import imutils
import time
import dlib
import threading

# Function to perform face recognition (simulated)
def do_recognize_person(face_names, face_id):
    time.sleep(2)
    face_names[face_id] = "Person " + str(face_id)

# Function to perform face detection in a separate thread
def detect_faces():
    face_trackers = {}  # Dictionary to store the correlation trackers and face IDs
    face_names = {}
    frame_counter = 0
    current_face_id = 0

    while True:
        ret, frame = cap.read()
        frame = imutils.resize(frame, width=640, height=440)

        # Update all trackers and remove the ones with low tracking quality
        fids_to_delete = []
        for fid in face_trackers.keys():
            tracking_quality = face_trackers[fid].update(frame)

            # If tracking quality is low, mark for deletion
            if tracking_quality < 7:
                fids_to_delete.append(fid)

        for fid in fids_to_delete:
            print("Removing fid " + str(fid) + " from list of trackers")
            face_trackers.pop(fid, None)

        # Every 10 frames, perform face detection
        if (frame_counter % 2) == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                x_bar = x + 0.5 * w
                y_bar = y + 0.5 * h
                matched_fid = None

                for fid in face_trackers.keys():
                    tracked_position = face_trackers[fid].get_position()
                    t_x = int(tracked_position.left())
                    t_y = int(tracked_position.top())
                    t_w = int(tracked_position.width())
                    t_h = int(tracked_position.height())
                    t_x_bar = t_x + 0.5 * t_w
                    t_y_bar = t_y + 0.5 * t_h

                    if (
                        (t_x <= x_bar <= (t_x + t_w))
                        and (t_y <= y_bar <= (t_y + t_h))
                        and (x <= t_x_bar <= (x + w))
                        and (y <= t_y_bar <= (y + h))
                    ):
                        matched_fid = fid

                # If no matched fid, create a new tracker
                if matched_fid is None:
                    print("Creating new tracker " + str(current_face_id))
                    tracker = dlib.correlation_tracker()
                    tracker.start_track(
                        frame, dlib.rectangle(x - 10, y - 20, x + w + 10, y + h + 20)
                    )
                    face_trackers[current_face_id] = tracker

                    # Start a new thread for face recognition (simulated)
                    t = threading.Thread(
                        target=do_recognize_person, args=(face_names, current_face_id)
                    )
                    t.start()

                    current_face_id += 1

        # Draw rectangles and names on the frame
        for fid in face_trackers.keys():
            tracked_position = face_trackers[fid].get_position()
            t_x = int(tracked_position.left())
            t_y = int(tracked_position.top())
            t_w = int(tracked_position.width())
            t_h = int(tracked_position.height())
            cv2.rectangle(frame, (t_x, t_y), (t_x + t_w, t_y + t_h), (0, 165, 255), 2)

            if fid in face_names.keys():
                cv2.putText(
                    frame,
                    face_names[fid],
                    (int(t_x + t_w / 2), int(t_y)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                )
            else:
                cv2.putText(
                    frame,
                    "Detecting...",
                    (int(t_x + t_w / 2), int(t_y)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2,
                )

        # Display the frame
        cv2.imshow("Face Detection and Tracking", frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        frame_counter += 1

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Open the default camera (usually 0)
    cap = cv2.VideoCapture(0)

    # Initialize MTCNN module
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Print message based on GPU availability
    if torch.cuda.is_available():
        print(
            f"GPU found and can be used. Using GPU: {torch.cuda.get_device_name(0)}"
        )
    else:
        print("No GPU found. Using CPU.")

    detector = MTCNN(keep_all=True, device=device, post_process=False)

    # Load the face cascade classifier
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Create a thread for face detection and tracking
    detection_thread = threading.Thread(target=detect_faces)
    detection_thread.start()

    # Wait for the detection thread to finish
    detection_thread.join()
