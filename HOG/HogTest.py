import cv2
import numpy as np

# Initialize HOG descriptor with default people detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

USE_MOTION_FILTERING = True     # Toggle motion-based detection on/off
CONFIDENCE_THRESHOLD = 0.6      # Only draw boxes above this score (0.0 - 1.0)

# Open camera (change index if needed)
cap = cv2.VideoCapture(0)

# Set high resolution (1280x720)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  #Try 640 x 480 or 1280 by 720
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) #1280 by 720 seems to be too high res to be fast

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

print("Press 'q' to quit.")
previous_gray = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Optional: improve performance with grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    motion_detected = True  #Default value set

     # === MOTION DETECTION ===
    if USE_MOTION_FILTERING:
        if previous_gray is not None:
            diff = cv2.absdiff(previous_gray, gray)
            thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
            motion_score = np.sum(thresh) / 255
            motion_detected = motion_score > 5000  #Can change lower if not sensitive enough
        previous_gray = gray.copy()

    
    if motion_detected:
        # Detect humans
        boxes, weights = hog.detectMultiScale(
            gray,
            winStride=(4, 4),
            padding=(8, 8),
            scale=1.03  # Try 1.01 for very small/far-away people
        )

    # Normalize confidence scores (for display)
    if weights is not None and len(weights) > 0:
        max_weight = max(weights)
    else:
        max_weight = 1  # Prevent divide by zero

    # Draw bounding boxes and confidence %
    for i, (x, y, w, h) in enumerate(boxes):
        if weights[i] > CONFIDENCE_THRESHOLD:        #Still tuning to between 0.5-1.0
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Normalize weight to a 0?100% range
        confidence = int((weights[i] / max_weight) * 100)

        # Report the quality of the match (not confidence, just how well matched the Haar cascade)
        text = f"{confidence}%"
        cv2.putText(frame, text, (x, y + h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show result
    cv2.imshow("Humans", frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()

 
