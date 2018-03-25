import cv2

class Detector:
    MIN_SIZE = (130, 150)
    MAX_SIZE = (580, 440)

    #MIN_SIZE = (350, 330)
    #MAX_SIZE = (950, 400)

    def __init__(self):
        self.cascade = cv2.CascadeClassifier('app/cascade_226.xml')

    def search_on(self, frame):
        exp = cv2.resize(frame, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(exp, cv2.COLOR_BGR2GRAY)
        birds = self.cascade.detectMultiScale(gray, 1.05, 2,
                                              minSize=self.MIN_SIZE, maxSize=self.MAX_SIZE)
        return birds
