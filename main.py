# Main Function for the Watchfull Webcams project
# 4/8/2025
# Evan Grover & Adam Kerkermeyer

import cv2
import os
import time

#dictonary like an enum, holds the position of the a person in a specific cammera frame

class camera_state:
    @property
    def state(self);
        return self._state

    @state.setter
    def state(self, value):
        if isinstance(value, int) and value >= 0 and value <= 4:
            self._state = value
        else:
            raise TypeError("Camerra state should be number  0 <= x <= 4")

def main():
    print(time.gmtime())

#Only run the main fucntion if this file is the one called
if __name__ == "__main__":
    main()

