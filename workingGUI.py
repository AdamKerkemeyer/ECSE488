# Main Function for the Watchfull Webcams project
# 4/8/2025
# Evan Grover & Adam Kerkermeyer

import cv2
import os
import time
import numpy as np
#for GUI
import tkinter as tk
from tkinter import scrolledtext, Toplevel, Label

from PIL import Image, ImageTk   #For PNG metadata strop to prevent libpng incorrect sRGB errors.
import threading
import contextlib

pause_polling = False       #global flag to control if we are checking all cameras. Operates on human interrupt.

#this will contain any data  for keeping variables between calls of get_distance
class detection_data:
    def __init__(self):
        print("this is a placeholder Adam pls fill me in")

def safe_open_cam(source, width = 640, height = 480, fps = 10):
    # temporarily silence all stderr output, this prevents warnings that the camera is in use popping up when you  try to access the camera with the GUI but the camera is currently being polled
    with open(os.devnull, 'w') as devnull, contextlib.redirect_stderr(devnull):
        cap = cv2.VideoCapture(source, cv2.CAP_V4L2)

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
        self.last_affirmed_2 = time.time()
        self.last_affirmed_3 = time.time()
        self.last_affirmed_4 = time.time()
    #state is basically an emun
    #1: no person in frame
    #2: person in frame is farther than 50m
    #3: person in frame is inbetween 10m and 50m from cammera
    #4: person in frame is closer than 10m 

    #logic for state changes, It is not neccessarily if distance setpoint hit chage state
    #See state trasnition table
    #Will update the VideoWriter (self.writer) to reflect the new framereate if needed
    def update_state(self, distance):
        path = "recordings"
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")

        if self.state == 1:#Adam: did u mean state = 1 here not state == 0? #state 1 
            if distance > 0:                                                #transition to 2
                self.state = 2
                self.last_affirmed_2 = time.time()
                write_log_entry(f"{self.name}: State changed from 1 to 2, person detected at {distance:.2f}m")
        elif self.state == 2:                                               #state 2
            if distance >= 50:                                              #no change
                self.last_affirmed_2 = time.time()
            elif distance < 50:                                             #transition to state 3
                self.state = 3
                self.last_affirmed_3 = time.time()
                os.makedirs(os.path.join(path, self.name), exist_ok = True)
                videoName = os.path.join(path, self.name, f"{timestamp}_lowfps.avi")
                #videoName = path+ "/" + self.name + "/" + time.asctime(time.localtime()) + " low fps"
                self.writer.open(videoName, self.codec, 5, self.framesize, True)
                write_log_entry(f"{self.name}: State changed from 2 to 3, person detected at {distance:.2f}m, video started: {videoName}")
            elif distance < 0 and self.last_affirmed_2 < time.time() - 5:        #transition to state 1
                self.state = 1
                write_log_entry(f"{self.name}: State fallback (2 to 1), no person detected")
        elif self.state == 3:                                                  #state 3
            if distance < 50 and distance >= 10:                            #no change
                self.last_affirmed_3 = time.time()
            elif distance < 10:                                             #transition to state 4
                self.state = 4
                self.last_affirmed_4 = time.time()
                os.makedirs(os.path.join(path, self.name), exist_ok = True)
                videoName = os.path.join(path, self.name, f"{timestamp}_highfps.avi")
                #videoName = path + "/" + self.name + "/" + time.asctime(time.localtime()) + " high fps"
                self.writer.open(videoName, self.codec, 15, self.framesize, True)
                write_log_entry(f"{self.name}: State changed from 3 to 4, person detected at {distance:.2f}m, video started: {videoName}")
            elif distance < 0 and self.last_affirmed_3 < time.time() - 5:        #transition to state 1
                self.state = 1
                self.writer.release()
                write_log_entry(f"{self.name}: State fallback (3 to 1), no person detected, video writer released")
            elif distance >= 50 and self.last_affirmed_3 < time.time() - 2:      #transition to state 2
                self.state = 2
                self.last_affirmed_2 = time.time()
                self.writer.release()
                write_log_entry(f"{self.name}: State fallback (3 to 2), no person detected, video writer released")
        elif self.state == 4:                                                  #state 4
            if distance < 10 and distance >= 0:                              #no change
                self.last_affirmed_4 = time.time()
            elif distance < 0 and self.last_affirmed_4 < time.time() - 5:         #transition to state 1
                self.state = 1
                self.writer.release()
                write_log_entry(f"{self.name}: State fallback (4 to 1), no person detected, video writer released")
            elif distance >= 10 and self.last_affirmed_4 < time.time() - 2:       #transition to state 3
                self.state = 3
                self.last_affirmed_3 = time.time()
                os.makedirs(os.path.join(path, self.name), exist_ok = True)
                videoName = os.path.join(path, self.name, f"{timestamp}_lowfps.avi")
                #videoName = path + "/" + self.name + "/" + time.asctime(time.localtime()) + " low fps"
                self.writer.open(videoName, self.codec, 5, self.framesize, True)
                write_log_entry(f"{self.name}: State fallback (4 to 3), no person detected, video started: {videoName}")

#Will write to the file system with the correct data rate
def save_footage(camera, path):
    cap = safe_open_cam(camera.source)
    if cap is None:
        print("Error in save footage function.")
        return
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("WARNING, Frame capture failed during save footage function.")
        return

    if camera.state in [3, 4]: #these are the video capture mode. The writter handles the framerate
        if camera.writer.isOpened():
            #_ , frame = camera.cap.read()
            camera.writer.write(frame)
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

    with open(log, "a") as log_file:     #Open log in append mode 
        log_file.write(log_entry)

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
        
    def business_logic():
        while True:
            if pause_polling:
                time.sleep(0.2)
                continue
            for camera in cameras:
                d = poll_distance(camera, net)
                camera.update_state(d)
                save_footage(camera, storage_path)

                    #end the program after 3 seconds
                    #  if time.time() > start_time + 3:
                    #     program_terminate = True  
            time.sleep(0.01) #throttle CPU

    threading.Thread(target=business_logic, daemon=True).start()

    open_gui(cameras)          #open GUI in the main thread.

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
def open_gui(cameras):
    gui = tk.Tk()
    gui.title("Watchful Webcams Panel")

    log_view = scrolledtext.ScrolledText(gui, width = 80, height = 20)      #Set log box size in GUI
    log_view.pack(padx = 10, pady = 10)
    #Log Buttons
    refresh_btn = tk.Button(gui, text="Refresh Log", command=lambda: load_log(log_view))
    refresh_btn.pack(pady=5)
    clear_btn = tk.Button(gui, text="Clear Log", command=lambda: clear_log(log_view))
    clear_btn.pack(pady=5)
    #Camera Buttons
    btn_frame = tk.Frame(gui)
    btn_frame.pack(pady = 10)
    for cam in cameras:
        tk.Button(
                btn_frame,
                text=f"{cam.name}",
                command=lambda c=cam: open_camera_window(c, gui)
            ).pack(side=tk.LEFT, padx=5)
    load_log(log_view)
    gui.mainloop()

def load_log(widget):
    try:
        with open("activity_log.txt", "r") as f:
            widget.delete(1.0, tk.END)
            widget.insert(tk.END, f.read())
    except FileNotFoundError:
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, "No log found. \n")

def clear_log(widget):
    wipe_log()
    widget.delete(1.0, tk.END)
    widget.insert(tk.END, "LOG CLEARED.\n")

def open_camera_window(camera, parent):
    global pause_polling
    if pause_polling:
        return
    pause_polling = True
    top = Toplevel(parent)
    top.title(f"Live: {camera.name}")
    waiting_lbl = Label(top, text=f"waiting for camera to become avaliable...")
    waiting_lbl.pack

    stop = threading.Event()

    def on_close():
        stop.set()
        #Do not try to release a camera that never successfully opened
        if 'cap' in locals() and cap is not None:
            cap.release()
        top.destroy()
        global pause_polling
        pause_polling = False
    top.protocol("WM_DELETE_WINDOW", on_close)

    cap = None
    while not stop.is_set():        #Try and open the camera (it may be being polled currently)
        cap = safe_open_cam(camera.source)
        if cap:
            break
        time.sleep(0.1)

    if stop.is_set() or cap is None:    #bail if user closes window
        return
    waiting_lbl.destroy()
    lbl = Label(top)
    lbl.pack()

    if cap is None:
        write_log_entry(f"Failed to open camera {camera.source}")
        on_close()
        return

    def update_frame():
        if stop.is_set():
            return
        ret, frame = cap.read()
        if ret:
            img = ImageTk.PhotoImage(
                    Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            )
            lbl.img = img
            lbl.config(image=img)
        # schedule next frame
        lbl.after(30, update_frame)

    update_frame()

#Only run the main fucntion if this file is the one called
if __name__ == "__main__":
    main()

