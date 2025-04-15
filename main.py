# Main Function for the Watchfull Webcams project
# 4/8/2025
# Evan Grover & Adam Kerkermeyer

import cv2
import os
import time
import numpy as np
#for GUI
import tkinter as tk
from tkinter import scrolledtext

from PIL import Image   #For PNG metadata strop to prevent libpng incorrect sRGB errors.
import threading

pause_polling = False       #global flag to control if we are checking all cameras. Operates on human interrupt.

#this will contain any data  for keeping variables between calls of get_distance
class detection_data:
    def __init__(self):
        print("this is a placeholder Adam pls fill me in")

def safe_open_cam(source, width = 640, height = 480, fps = 10):
    cap = cv2.VideoCapture(source,cv2.CAP_V4L2)
    if not cap.isOpened():
        print(f"Error, could not open video source: {source}")
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    return cap

#This should prevent the libpng incorrect sRGB errors, ultimately these files should be stored as JPEG.
def safe_write_png(path, frame):
    filename = time.strftime("%Y-%m-%d_%H-$M-%S") + ".png"
    filepath = os.path.join(path, filename)
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        img.save(filepath, format="PNG", compress_level = 3)
    except Exception as e:
        print(f"Error, PNG save failed: {e}")

class camera_state:
    def __init__(self, source, data, name):
        self.source = source 
        self.cap = safe_open_cam(source)
        if self.cap is None:
            #Something not working then, initialize framesize to default anyways
            self.framesize = (640, 480)
            self.codec = cv2.VideoWriter_fourcc(*'MJPG')
        else:
            self.framesize = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self.codec = int(self.cap.get(cv2.CAP_PROP_FOURCC))
            self.cap.release()

        self.writer = cv2.VideoWriter()
        self.data = data
        self.name = name
        
        self.state = 1
        self.last_pic_time = time.time()
        self.last_affirmed_1 = time.time()
        self.last_affirmed_2 = time.time()
        self.last_affirmed_3 = time.time()
"""
    #state is basically an emun
    #1: no person in frame
    #2: person in frame is farther than 50m
    #3: person in frame is inbetween 10m and 50m from cammera
    #4: person in frame is closer than 10m 
""" 
"""
    state = 1
    #last_pic_time is the time the last picuture was take so I can take a picture every 3 seconds
    last_pic_time = time.time()
    #last seen times for each state
    last_affirmed_2 = time.time()
    last_affirmed_3 = time.time()
    last_affirmed_4 = time.time()
"""
    #logic for state changes, It is not neccessarily if distance setpoint hit chage state
    #See state trasnition table
    #Will update the VideoWriter (self.writer) to reflect the new framereate if needed
    def update_state(self, distance):
        path = "recordings"
        timestamp = time.strftime("%Y-%m-d_%H-%M-%S")

        if self.state == 1:#Adam: did u mean state = 1 here not state == 0? #state 1 
            if distance > 0:                                                #transition to 2
                self.state = 2
                self.last_affirmed_2 = time.time()
        elif self.state == 2:                                               #state 2
            if distance >= 50:                                              #no change
                self.last_affirmed_2 = time.time()
            elif distance < 50:                                             #transition to state 3
                self.state = 3
                self.last_affirmed_3 = time.time()
                videoName = os.path.join(path, self.name, f"{timestamp}_lowfps.avi")
                #videoName = path+ "/" + self.name + "/" + time.asctime(time.localtime()) + " low fps"
                self.writer.open(videoName, self.codec, 5, self.framesize, True)
            elif distance < 0 and self.last_affirmed_2 < time.time() - 5:        #transition to state 1
                self.state = 1
        elif self.state == 3:                                                  #state 3
            if distance < 50 and distance >= 10:                            #no change
                self.last_affirmed_3 = time.time()
            elif distance < 10:                                             #transition to state 4
                self.state = 4
                self.last_affirmed_4 = time.time()
                videoName = os.path.join(path, self.name, f"{timestamp}_highfps.avi")
                #videoName = path + "/" + self.name + "/" + time.asctime(time.localtime()) + " high fps"
                self.writer.open(videoName, self.codec, 15, self.framesize, True)
            elif distance < 0 and self.last_affirmed_3 < time.time() - 5:        #transition to state 1
                self.state = 1
                self.writer.release()
            elif distance >= 50 and self.last_affirmed_3 < time.time() - 2:      #transition to state 2
                self.state = 2
                self.last_affirmed_2 = time.time()
                self.writer.release()
        elif self.state == 4:                                                  #state 4
            if distance < 10 and distance >= 0:                              #no change
                self.last_affirmed_4 = time.time()
            elif distance < 0 and self.last_affirmed_4 < time.time() - 5:         #transition to state 1
                self.state = 1
                self.writer.release()
            elif distance >= 10 and self.last_affirmed_4 < time.time() - 2:       #transition to state 3
                self.state = 3
                self.last_affirmed_3 = time.time()
                videoName = os.path.join(path, self.name, f"{timestamp}_lowfps.avi")
                #videoName = path + "/" + self.name + "/" + time.asctime(time.localtime()) + " low fps"
                self.writer.open(videoName, self.codec, 5, self.framesize, True)

#Will write to the file system with the correct data rate
def save_footage(camera, path):
    cap = safe_open_cam(camera.source)
    if cap is None:
        print("Error in save footage function.")
        return
    ret, frame = cap.read()
    cap.release()
    if not ret
        print("WARNING, Frame capture failed during save footage function.")
        return

    if camera.state in [3, 4]: #these are the video capture mode. The writter handles the framerate
        if camera.writer.isOpened:
            #_ , frame = camera.cap.read()
            camera.writer(frame)
        else:
            print("Error: Camera mode dependent on writer was used without opening the writer. No video will be saved")
    elif camera.state == 2 and camera.last_pic_time < (time.time() - 3) : # 1/3 hz picture mode, only once ever 3 sec MAX
            camera.last_pic_time = time.time()
           # _ , frame = camera.cap.read()
           # cv2.imwrite(path + "/" + camera.name + "/" + time.asctime(time.localtime()), frame)
           save_path = os.path.join(path, camera.name)
           os.makedirs(save_path, exist_ok = True)
           safe_write_png(save_path, frame)
    #We don't do image capture on state 1 so there is nothing to do here

log = "activity_log.txt"

def write_log_entry(message):
    #Append a message to the log:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_entry = f"[{timestamp}] {message} \n"

    with open(log, "a") as log:     #Open log in append mode 
        log.write(log_entry)

def wipe_log():
    #Clear log
    open(log, "w").close()

def main():
    #setup
    storage_path = "recordings"
    config_path  = "./YOLO4TINY/yolov4-tiny.cfg"
    weights_path = "./YOLO4TINY/yolov4-tiny.weights"

    net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    #camera_0.avi & ect. are placeholders, they should really by be like /dev/video0
    cameras = [
        camera_state(0, detection_data(), "camera0"),
        camera_state(2, detection_data(), "camera1"),
        camera_state(4, detection_data(), "camera2"),
        camera_state(6, detection_data(), "camera3")
    ]

       start_time = time.time()
    
    #In order for program to work, tk must be in main thread, and business logic must be threaded.

    #Business logic
    program_terminate = False           #No longer using this value.
    
    def business_logic():
        while True:
            if not pause_polling:
                for camera in cameras: 
                    camera.update_state(poll_distance(camera, net))
                    save_footage(camera, storage_path)

                    #end the program after 3 seconds
                    #  if time.time() > start_time + 3:
                    #     program_terminate = True       

    threading.Thread(target=business_logic, daemon=True).start()

    open_gui()          #open GUI in the main thread.
        



#polls the video feed of camera and returns the distance of a target in meters
# -1 means no target detected
# Returns a float
# All checking and probablity logic needs to be figured out by this point. 
# This function should be 100% accurate on if there is a person or not
# it should be within +-10m @ the 50m distance
# it should be within +-5m @ the 10m mark
def poll_distance(camera, net):
    cap = safe_open_cam(camera.source)
    if cap is None:
        return -2   #Already return -1 if no person detected
    #cap = cv2.VideoCapture(camera.source)
    ret, frame = cap.read()
    cap.release()       #poll distance was missing this cap release!

    if not ret or frame is None:
        return -3

    height, width = frame.shape[:2]

    # Create blob and perform forward pass
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(net.getUnconnectedOutLayersNames())

    boxes, results, confidences = [], [], []

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Only detect 'person' class (class_id = 0)
            if class_id == 0 and confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                results.append({'x': x, 'y': y, 'w': w,'h': h,'confidence': confidence})


    # Non-max suppression to eliminate overlapping boxes
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    if len(indices) > 0:
        final_results = []
        for i in indices:
            i = i[0] if isinstance(i, int) else i
            final_results.append(results[i])
        results =  final_results
    print(results)
    if len(results) > 0:
        distance = -0.03125*(results[0]['h'] - 700) + 20
        print(distance)
        return distance
    else:
        print(-1)
        return -1

#GUI Code:
def show_live(source):
    global pause_polling
    pause_polling = True

    cap = safe_open_cam(source)
    if cap is None:
        print("ERROR, show live camera button failed to open camera {source}")
        return
    
    #Define parameters (Not necessary, can remove all of these)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    #cap.set(cv2.CAP_PROP_FPS, 10)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow(f"Camera {source}", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pause_polling = False

def open_gui():
    def load_log():
        try:
            with open(log, "r") as log_file:        #Names cannot match, log is global variable
                log_content = log_file.read()
                log_view.delete(1.0, tk.END)
                log_view.insert(tk.END, log_content)
        except FileNotFoundError:
            log_view.insert(tk.END, "Log file was not found / No log has been generated.\n")
    
    def launch_camera(index):
        cam_sources = [0, 2, 4, 6]      #Not sure if I can do this with the camera objects you already made Evan
        threading.Thread(target = show_live, args=(cam_sources[index],), daemon=True).start()

    gui = tk.Tk()
    gui.title("Watchful Webcams Panel")

    log_view = scrolledtext.ScrolledText(gui, width = 80, height = 20)      #Set log box size in GUI
    log_view.pack(padx = 10, pady = 10)

    btn_frame = tk.Frame(gui)
    btn_frame.pack(pady = 10)

    for i in range(4):                                                      #Make Buttons
        tk.Button(btn_frame, text=f"Camera {i+1}", command=lambda i=i: launch_camera(i)).pack(side=tk.LEFT, padx=5)

    refresh_btn = tk.Button(gui, text="Refresh Log", command=load_log)
    refresh_btn.pack(pady=5)

    load_log()
    gui.mainloop()


#Only run the main fucntion if this file is the one called
if __name__ == "__main__":
    main()

