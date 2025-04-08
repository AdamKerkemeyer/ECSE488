import cv2
import os
import time

# Initialize the background subtractor
fgbg = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=100, detectShadows=True)

# Define the webcam device
camera_index = "/dev/video0"  # Adjust if necessary
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print(f"Error: Could not open camera {camera_index}")
    exit()

# Capture an initial image
ret, frame = cap.read()
if not ret:
    print("Error: Could not capture image.")
    cap.release()
    exit()

# Save the temporary image
image_path = "temp_capture.jpg"
cv2.imwrite(image_path, frame)

# Convert to grayscale
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# Apply background subtraction to detect movement
fgmask = fgbg.apply(frame)

# Apply thresholding to remove noise
_, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)

# Find contours (possible human outlines)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter out small contours (to detect people at a distance)
person_detected = False
for contour in contours:
    area = cv2.contourArea(contour)
    if area > 3000:  # Adjust this value for better distance tuning
        person_detected = True
        break

# Print result and delete image if no person is detected
if person_detected:
    print("Person Detected!")
else:
    #os.remove(image_path)
    print("No person detected. Image deleted.")

# Release camera
cap.release()

