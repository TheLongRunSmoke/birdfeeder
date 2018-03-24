import time

import picamera

from app.cam.ICamera import ICamera


class PiCamera(ICamera):

    def __init__(self) -> None:
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1920, 1080)
        self.camera.framerate = 30
        self.feed = PiRGBArray(self.camera, size = (1920,1080))
        time.sleep(0.1)

    def retrieve(self):
        for frame in self.camera.capture_continuous(self.feed, format="bgr", use_video_port=True):
            return frame.array

    def get_exposure(self):
        pass

    def auto_exposure(self, frame):
        pass