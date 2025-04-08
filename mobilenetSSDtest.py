import cv2
import numpy as np

# Load MobileNet SSD model
prototxt_path = "MobileNetSSD_deploy.prototxt"
caffe_model_path = "MobileNetSSD_deploy.caffemodel"

net = cv2.dnn.readNetFromCaffe(prototxt_path, caffe_model_path)

# Open webcam
camera_index = "/dev/video0"  # Adjust as needed
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print(f"Error: Could not open camera {camera_index}")
    exit()

# MobileNet SSD class labels (detect only "person")
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    (h, w) = frame.shape[:2]

    # Prepare the image for detection
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.4:  # Confidence threshold
            class_index = int(detections[0, 0, i, 1])
            if CLASSES[class_index] == "person":
                # Get bounding box
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # Estimate distance based on bounding box height
                box_height = endY - startY
                estimated_distance = round(5000 / box_height, 2)  # Adjust for calibration

                # Draw rectangle and label
                label = f"Person: {int(confidence * 100)}% - {estimated_distance} ft"
                cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                cv2.putText(frame, label, (startX, startY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Show the video feed
    cv2.imshow("Person Detection", frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
