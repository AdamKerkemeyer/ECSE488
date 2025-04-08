import cv2
import os
import time
import imutils

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

# Initializing the HOG person
# detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
  
# Reading the Image
image = cv2.imread('temp_capture.jpg')
  
# Resizing the Image
image = imutils.resize(image,
                       width=min(400, image.shape[1]))
  
# Detecting all the regions in the 
# Image that has a pedestrians inside it
(regions, _) = hog.detectMultiScale(image, 
                                    winStride=(4, 4),
                                    padding=(4, 4),
                                    scale=1.05)
  
# Drawing the regions in the Image
for (x, y, w, h) in regions:
    cv2.rectangle(image, (x, y), 
                  (x + w, y + h), 
                  (0, 0, 255), 2)
 
# Showing the output Image
cv2.imshow("Image", image)
cv2.waitKey(0)
  
cv2.destroyAllWindows()
