import cv2


class Detector:
    MIN_SIZE = (130, 150)
    MAX_SIZE = (580, 440)

    def __init__(self):
        self.cascade = cv2.CascadeClassifier('cascade_226.xml')

    def search_on(self, frame):
        # exp = cv2.resize(frame, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_LINEAR)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        birds = self.cascade.detectMultiScale(gray, 1.05, 7,
                                              minSize=self.MIN_SIZE, maxSize=self.MAX_SIZE)
        return birds
