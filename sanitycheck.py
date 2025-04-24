#test file to test random code snippets to check I'm not insan
import cv2
import time

# Open the webcam (0 is the default camera)
cap = cv2.VideoCapture(2)
print("not a video capture problem")

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Get the frame width and height
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can use other codecs like 'MJPG', 'MP4V', etc.
out = cv2.VideoWriter('output.avi', fourcc, 10.0, (frame_width, frame_height))

next_record_time = time.time()

while True:
    #print("got to while loop")
    #print(time.time())
    # Capture frame-by-frame
    if next_record_time <= time.time():
        print("caputureing frame")
        next_record_time += 0.5
        ret, frame = cap.read()

    # If frame is read correctly, ret is True
        if not ret:
            print("Error: Failed to capture frame.")
            break

    # Write the frame to the video file
        out.write(frame)

    # Display the resulting frame
    #cv2.imshow('Webcam Video', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release everything when done
cap.release()
out.release()
cv2.destroyAllWindows()
