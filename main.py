# Main Function for the Watchfull Webcams project
# 4/8/2025
# Evan Grover & Adam Kerkermeyer

import cv2
import os
import time

#this will contain any data  for keeping variables between calls of get_distance
class detection_data:
    def __init__(self):
        print("this is a placeholder Adam pls fill me in")

class camera_state:
    def __init__(self, source, data):
        self.source = source
        self.cap = cv2.VideoCapture(source)
        self.data = data
    #state is basically an emun
    #1: no person in frame
    #2: person in frame is farther than 50m
    #3: person in frame is inbetween 10m and 50m from cammera
    #4: person in frame is closer than 10m
    state = 1
    #lscan_time is the sys_time at the last time this cammera was evaluated. It it initially 0
    #to force an imediate scan on system poweron
    lscan_time = time.time()

#This should analyze one frame from the specified camera and give me the distance of the person in the frame. If there are
#no people in the frame it should return -1. 
#camera_state class will contain an atribute .cap, this is your VideoCapture object
#it will also contain an atribute .data. This is the class you will create (detection_data) containing your across frame data
def get_distance(camera):
    print("this is a placeholder Adam pls fill me in")

def main():
    #setup
    camera0 = camera_state("camera_0.avi", detection_data())
    #camera1 = camera_state()
    #camera2 = camera_state()
    #camera3 = camera_state()

    #cameras = [camera0, camera1, camera2, camera3]

    start_time = time.time()

    filename = "test_video.avi"
    if os.path.exists(filename):
        os.remove(filename)
        print("old video deleted")

    writer = cv2.VideoWriter()
    codec = int(camera0.cap.get(cv2.CAP_PROP_FOURCC))
    fps = camera0.cap.get(cv2.CAP_PROP_FPS)
    framesize = (int(camera0.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(camera0.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    outputVideo = cv2.VideoWriter()
    outputVideo.open("test_video.avi", codec, fps, framesize, True)
    if not outputVideo.isOpened():
        print("output video did not open")
    frame = cv2.UMat()

    #Business logic
    program_terminate = False
    while not program_terminate:
        _ , frame = camera0.cap.read()
        outputVideo.write(frame)

        #end the program after 3 seconds
        if time.time() > start_time + 3:
            program_terminate = True
        
        



#polls the video feed of camera and returns the distance of a target in meters
# -1 means no target detected
# Returns a float
# All checking and probablity logic needs to be figured out by this point. 
# This function should be 100% accurate on if there is a person or not
# it should be within +-10m @ the 50m distance
# it should be within +-5m @ the 10m mark
# it will be ran once a second (this could be adjusted) for each camera, so it needs to complete in t < 0.25s
# but should really complete in less than that to give the rest of the program time to run
#def poll_distance(camera):


#Only run the main fucntion if this file is the one called
if __name__ == "__main__":
    main()

