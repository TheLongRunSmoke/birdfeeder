import numpy
import cv2

from app.cam.ICamera import ICamera


class WebCamera(ICamera):

    def __init__(self, camera_id) -> None:
        self.feed = cv2.VideoCapture(camera_id)
        self.feed.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.feed.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        self.feed.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # manual mode
        self.feed.set(cv2.CAP_PROP_EXPOSURE, 0.005)
        self.skipCounter = 0

    def retrieve(self):
        while True:
            if self.feed.grab():
                _, frame = self.feed.retrieve()
                return frame

    def auto_exposure(self, frame):
        resize = cv2.resize(frame, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_LINEAR)
        yuv_frame = cv2.cvtColor(resize, cv2.COLOR_BGR2YUV)
        self.skipCounter = self.skipCounter - 1
        if self.skipCounter < 1:
            lumaAvg = numpy.average(yuv_frame[:, :, 0])
            # print(lumaAvg, self.getExposure())
            if (lumaAvg > 190) or (lumaAvg < 170):
                self.skipCounter = 2
                newExposure = 180 * self.get_exposure() / lumaAvg
                if newExposure < 1:
                    # print("newExposure: %f" % newExposure)
                    self.feed.set(cv2.CAP_PROP_EXPOSURE, newExposure)
            return lumaAvg
        return 0

    def get_exposure(self):
        exp = self.feed.get(cv2.CAP_PROP_EXPOSURE)
        return exp
