import cv2
import numpy as np

# Initialize HOG detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Open webcam
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

# Read first frame
ret, prev_frame = cap.read()
if not ret or prev_frame is None:
    print("Error: Could not read first frame")
    cap.release()
    exit()

RESOLUTION = (1024, 768)
prev_frame = cv2.resize(prev_frame, RESOLUTION)
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        break

    frame = cv2.resize(frame, RESOLUTION)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Motion detection
    frame_delta = cv2.absdiff(prev_gray, gray)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    motion_level = cv2.countNonZero(thresh)

    motion_detected = motion_level > 5000  # Adjust threshold if needed

    if motion_detected:
        print("Motion detected ? running HOG on full frame")

        try:
            # Ensure frame is contiguous for OpenCV
            full_frame = np.ascontiguousarray(frame)

            boxes, weights = hog.detectMultiScale(
                full_frame,
                winStride=(4, 4),
                padding=(8, 8),
                scale=1.04
            )

            for (x, y, w, h) in boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        except Exception as e:
            print("HOG error:", e)
    else:
        print("No motion ? skipping HOG")

    # Overlay motion status
    status_text = "Motion detected" if motion_detected else "No motion detected"
    color = (0, 255, 0) if motion_detected else (0, 0, 255)
    cv2.putText(frame, status_text, (20, RESOLUTION[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Show the result
    cv2.imshow("HOG Detection (Motion Triggered)", frame)
    prev_gray = gray.copy()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

