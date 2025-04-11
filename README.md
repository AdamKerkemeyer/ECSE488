# ECSE488
## Overview
4 USB video camera project using OpenCV and YOLOv4-tiny on Pi 5.
We selected the Xcellon HDWC-WA10 Full HD Wide-Angle Webcam with a 2 MP resolution to be our cameras. We also selected a 4-port power optional USB 3.0 hub to connect all 4 webcams to the Raspberry Pi.
Distance from the target is estimated due to the lack of depth cameras using a linear relationship:

Distance = Subject Height * Focal Length /〖Subject Height)<sub>(# pixels)</sub>

## Finite State Machine
1.  Mode 1: No persons are detected; Raspberry Pi continues in Mode 1 and polls each camera sequentially. We plan to poll using 1 second video clips that the Haar cascade will analyze to identify bounding boxes, and if a bounding box is drawn it will have detected an Event 2, and move into Mode 2. 
2.	Mode 2: The target is passing by (bounding box is not increasing / distance estimation is not decreasing (within a certain error margin)). The Raspberry Pi will not poll other cameras while this camera is detecting an Event 2 so that it can detect if the target transitions to Event 1 (no targets detected) or Event 3 (bounding box is increasing). The Raspberry Pi will take one photo at the beginning (and potentially the end) of the Mode 2 cycle and store the images in JPEG format with timestamps for future review by the operator.
3.	Mode 3: The target is moving towards the camera. The Raspberry Pi will continue ignoring other cameras while this camera is detecting an Event 3 so it can detect if the target transitions to Mode 1, 2, or 4. It will begin recording Event 3 of the target in ½ the normal frame rate and store any video in MPEG format. 
a.	If Event 1 is detected (no targets) Mode 3 can still immediately transition to Mode 1 but it should continue to record for some time after in the event of a glitch in the Haar cascade, as it is unlikely a target will simply disappear when they are approaching the camera.
4.	Mode 4: The target continues to approach the camera. The Raspberry Pi will record video of the target, we may also implement a continuous recording function so that we can save the 30 seconds before the target was identified as Mode 4 video (higher quality) (or potentially event from the beginning of when the target was identified). Any recorded video will be compressed to MPEG format. Mode 4 is still directly accessible from Mode 1. For example, if the target has moved from in front of the North facing camera in Mode 4 to the West facing camera and is still approaching the warehouse. 
