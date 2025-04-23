#test file to test random code snippets to check I'm not insane
import cv2

# Open default camera (usually /dev/video0 on Linux)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Use V4L2 backend explicitly (optional)

if not cap.isOpened():
    print("❌ Failed to open camera.")
    exit()

print("✅ Camera opened. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to grab frame.")
        break

    print("showing frame")
    #cv2.imshow("Live Camera", frame)

    # Exit loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
