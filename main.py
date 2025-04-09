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
    def __init__(self, source, data, name):
        self.source = source #source of the video feed
        self.cap = cv2.VideoCapture(source)
        self.writer = cv3.VideoWriter()
        self.codec = int(self.cap.get(cv2.CAP_PROP_FOURCC))
        self.framesize = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.data = data #detection data storage
        self.name = name #name of the cammera
    #state is basically an emun
    #1: no person in frame
    #2: person in frame is farther than 50m
    #3: person in frame is inbetween 10m and 50m from cammera
    #4: person in frame is closer than 10m
    state = 1
    #last_pic_time is the time the last picuture was take so I can take a picture every 3 seconds
    last_pic_time = time.time()
    #last seen times for each state
    last_affirmed_2 = time.time()
    last_affirmed_3 = time.time()
    last_affirmed_4 = time.time()


    #logic for state changes, It is not neccessarily if distance setpoint hit chage state
    #See state trasnition table
    #Will update the VideoWriter (self.writer) to reflect the new framereate if needed
    def update_state(distance)
        if state == 0:                                                    #state 1
            if distance > 0:                                                #transition to 2
                state = 2
                last_affirmed_2 = time.time()
        elif state == 2:                                                  #state 2
            if distance >= 50:                                              #no change
                last_affirmed_2 = time.time()
            elif distance < 50:                                             #transition to state 3
                state = 3
                last_affirmed_3 = time.time()
                videoName = path + "/" + camera.name + "/" + time.asctime(time.localtime()) + " low fps"
                writer.open(videoName, codec, 5, framesize, True)
            elif distance < 0 and last_affirmed_2 < time.time() - 5:        #transition to state 1
                    state = 1
        elif state == 3:                                                  #state 3
            if distance < 50 and distance >= 10:                            #no change
                last_affirmed_3 = time.time()
            elif distance < 10:                                             #transition to state 4
                state = 4
                last_affirmed_4 = time.time()
                videoName = path + "/" + camera.name + "/" + time.asctime(time.localtime()) + " high fps"
                writer.open(videoName, codec, 15, framesize, True)
            elif distance < 0 and last_affirmed_3 < time.time() - 5:        #transition to state 1
                state = 1
                writer.release()
            elif distance >= 50 and last_affirmed_3 < time.time() - 2:      #transition to state 2
                state = 2
                last_affirmed_2 = time.time()
                writer.release()
        elif state == 4:                                                  #state 4
            if distance < 10 and distance >= 0:                              #no change
                last_affirmed_4 = time.time()
            elif distance < 0 and last_affirmed_4 < time.time() - 5:         #transition to state 1
                state = 1
                writer.release()
            elif distance >= 10 and last_affirmed_4 < time.time() - 2:       #transition to state 3
                state = 3
                last_affirmed_3 = time.time()
                videoName = path + "/" + camera.name + "/" + time.asctime(time.localtime()) + " low fps"
                writer.open(videoName, codec, 5, framesize, True)

#Will write to the file system with the correct data rate
def save_footage(camera, path):
    if camera.state == 4 or camera.state == 3: #these are the video capture mode. The writter handles the framerate
        if camera.writer.isOpened:
            _ , frame = camera.cap.read()
            camera.writer(frame)
        else:
            print("Error: Camera mode dependent on writer was used without opening the writer. No video will be saved")
    elif camera.state == 2: # 1/3 hz picture mode
        if camera.last_pic_time < time.time() - 3: #only take a picture every 3 seconds
            camera.last_pic_time = time.time()
            _ , frame = camera.cap.read()
            cv2.imwrite(path + "/" + camera.name + "/" + time.asctime(time.localtime()), frame)
    #We don't do image capture on state 1 so there is nothing to do here

#This should analyze one frame from the specified camera and give me the distance of the person in the frame. If there are
#no people in the frame it should return -1. 
#camera_state class will contain an atribute .cap, this is your VideoCapture object
#it will also contain an atribute .data. This is the class you will create (detection_data) containing your across frame data
def get_distance(camera):
    print("this is a placeholder Adam pls fill me in")
    return 0

def main():
    #setup
    storage_path = "recordings"
    #camera_0.avi & ect. are placeholders, they should really by be like /dev/video0
    camera0 = camera_state("camera_0.avi", detection_data(), "camera0")
    camera1 = camera_state("camera_1.avi", detection_data(), "camera1")
    camera2 = camera_state("camera_2.avi", detection_data(), "camera2")
    camera3 = camera_state("camera_3.avi", detection_data(), "camera3")

    cameras = [camera0, camera1, camera2, camera3]

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
        for camera in cameras: 
            camera.update_state(get_distance(camera))
            save_footage(camera, storage_path)

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

