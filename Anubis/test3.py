from facenet_pytorch import MTCNN
import torch
import cv2
import threading
import imutils

# Function to perform face detection in a separate thread
def detect_faces(cap, detector, new_width, new_height):
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame for face detection using imutils
        resized_frame = imutils.resize(frame, width=new_width, height=new_height)

        # Detect faces using MTCNN on the resized frame
        boxes, conf = detector.detect(resized_frame)

        if conf[0] is not None:
            for (x, y, w, h) in boxes:
                # Scale bounding box coordinates back to the original frame size
                x, y, w, h = int(x * (frame.shape[1] / new_width)), int(y * (frame.shape[0] / new_height)), int(w * (frame.shape[1] / new_width)), int(h * (frame.shape[0] / new_height))

                color = (0, 165, 0)
                stroke = 2
                text = f"Face detected: {conf[0]*100:.2f}%"
                
                # Decrease font size and adjust text position
                font_size = 0.5
                text_position = (x, y-10)
                
                cv2.putText(frame, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 0, 0), thickness=1)
                cv2.rectangle(frame, (x, y), (w, h), color, stroke)

        # Display the resulting frame (resized back to the original size)
        cv2.imshow('Face Detection with FaceNet', frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

# Close all windows
cv2.destroyAllWindows()

if __name__ == "__main__":
    # Open the default camera (usually 0)
    cap = cv2.VideoCapture(0)

    # Initialize MTCNN module
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Print message based on GPU availability
    if torch.cuda.is_available():
        print(f"GPU found and can be used. Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("No GPU found. Using CPU.")

    # Specify the new width and height for resizing
    new_width, new_height = 640, 480

    detector = MTCNN(keep_all=True, device=device, post_process=False)

    # Create a thread for face detection
    detection_thread = threading.Thread(target=detect_faces, args=(cap, detector, new_width, new_height))
    detection_thread.start()

    # Wait for the detection thread to finish
    detection_thread.join()

    # Release the capture object
    cap.release()
