import time

import picamera as pi
import picamera.array as pi_array

from app.cam.ICamera import ICamera


class PiCamera(ICamera):

    def __init__(self) -> None:
        self.camera = pi.PiCamera()
        size = (1920,1080)
        self.camera.resolution = size
        self.camera.framerate = 20
        self.camera.exposure_compensation = 6
        self.feed = pi_array.PiRGBArray(self.camera, size = size)
        time.sleep(0.1)

    def retrieve(self):
        self.camera.capture(self.feed, format="bgr")
        frame = self.feed.array
        self.feed.truncate(0)
        return frame

    def get_exposure(self):
        pass

    def auto_exposure(self, frame):
        pass
