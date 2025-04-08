import cv2

# Initialize HOG descriptor with default people detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Open camera (change index if needed)
cap = cv2.VideoCapture(0)

# Set high resolution (1280x720)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) #Try 640 x 480 or 1280 by 720
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Optional: improve performance with grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect humans
    boxes, weights = hog.detectMultiScale(
        gray,
        winStride=(4, 4),
        padding=(8, 8),
        scale=1.05  # Try 1.01 for very small/far-away people
    )

    # Normalize confidence scores (for display)
    if weights is not None and len(weights) > 0:
        max_weight = max(weights)
    else:
        max_weight = 1  # Prevent divide by zero

    # Draw bounding boxes and confidence %
    for i, (x, y, w, h) in enumerate(boxes):
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Normalize weight to a 0?100% range
        confidence = int((weights[i] / max_weight) * 100)

        # Report the quality of the match (not confidence, just how well matched the Haar cascade)
        text = f"{match}%"
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

 
