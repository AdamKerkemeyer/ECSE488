# Imports
import cv2

# Load the pre-trained HOG (Histogram of Oriented Gradients) human detection model
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Open the default webcam
cap = cv2.VideoCapture(0)

# Check if the webcam is available
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Main loop
while True:
    # Capture a frame
    ret, frame = cap.read()

    # Break if frame not read properly
    if not ret:
        print("Failed to grab frame.")
        break

    # Resize for better performance (optional)
    frame = cv2.resize(frame, (1280, 720))   #Originally 640, 480

    # Detect humans using the HOG model
    boxes, weights = hog.detectMultiScale(
        frame,
        winStride=(4, 4),
        padding=(16, 16),
        scale=1.04
    )

    # Draw bounding boxes around detected people
    for (x, y, w, h) in boxes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Show the frame in a window
    cv2.imshow("Human Detection", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

