import cv2
import time

# List of camera device paths (adjust if necessary)
cameras = ["/dev/video0", "/dev/video2", "/dev/video4", "/dev/video6"]

# Video settings
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30
RECORD_TIME = 4  # seconds

# Define codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*"XVID")

for i, cam in enumerate(cameras):
    print(f"Recording from {cam}...")

    # Open camera
    cap = cv2.VideoCapture(cam)
    if not cap.isOpened():
        print(f"Error: Could not open camera {cam}")
        continue

    # Set resolution and FPS
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    # Create output video file
    output_filename = f"camera_{i}.avi"
    out = cv2.VideoWriter(output_filename, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

    start_time = time.time()
    while time.time() - start_time < RECORD_TIME:
        ret, frame = cap.read()
        if not ret:
            print(f"Error: Could not read frame from {cam}")
            break
        out.write(frame)  # Write frame to file
        cv2.imshow(f"Recording {cam}", frame)  # Display recording feed

        # Stop recording if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Finished recording from {cam}, saved as {output_filename}")
