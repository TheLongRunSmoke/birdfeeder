import os, time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import asyncio
import numpy
from app import app
import cv2

class CV:

    def __init__(self):
        self.feed = cv2.VideoCapture(0)
        self.feed.set(cv2.CAP_PROP_FRAME_WIDTH,800)
        self.feed.set(cv2.CAP_PROP_FRAME_HEIGHT,600)
        # self.feed.set(cv2.CAP_PROP_SHARPNESS,1)
        self.feed.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.25) # manual mode
        self.feed.set(cv2.CAP_PROP_EXPOSURE, 0)
        self.isUpdated = False
        self.time = 0
        self.fps = 0
        self.streamBuf = None
        self.avg = DequeAverager(3)
        
        self.bgSubtractor = cv2.createBackgroundSubtractorMOG2()
        self.history = 100
        
        self.loop = asyncio.get_event_loop()
        self.pool = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
        self.loop.run_in_executor(self.pool, self.process)
        self.loop.close()

    def get(self):
        while True:
            if self.isUpdated:
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' \
                   + self.imageBuf.tostring() + b'\r\n')
                self.isUpdated = False

    def process(self):
        while True:
            if self.feed.grab() == True:
                
                if(self.time == int(time.time())):
                    self.fps += 1
                else:
                    print('FPS: %i' % (self.fps))
                    self.time = int(time.time())
                    self.fps=0
            
                rval, frame = self.feed.retrieve()

                self.autoExposure(cv2.cvtColor(frame, cv2.COLOR_BGR2YUV))

                #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                mask = self.bgSubtractor.apply(frame, learningRate=1.0/self.history)
                mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                
                                
                if not self.isUpdated:
                    ret, self.imageBuf = cv2.imencode('*.jpg', frame)
                    ret, self.imageBuf = cv2.imencode('*.jpg', \
                                        numpy.concatenate((frame, mask & frame), axis=0))
                    self.isUpdated = True

    def autoExposure(self, yuv_frame):
        lumaAvg = numpy.average(yuv_frame[:,:,0])
        self.avg.append(lumaAvg) 
        avg = self.avg.avg()
        print(avg, lumaAvg, self.getExposure())
        if (avg > 180):
            self.decExposure()
        if (avg < 130):
            self.incExposure()

    def getExposure(self):
        exp = self.feed.get(cv2.CAP_PROP_EXPOSURE)
        return exp

    def incExposure(self):
        exp = self.getExposure() + 0.0003
        if exp <= 1:
            self.feed.set(cv2.CAP_PROP_EXPOSURE, exp)
            
    def decExposure(self):
        exp = self.getExposure() - 0.0003
        if exp >= 0:
            self.feed.set(cv2.CAP_PROP_EXPOSURE, exp)


from collections import deque

class DequeAverager(deque):

    def __init__(self, size) -> None:
        super().__init__()
        self.stackSize = size

    def append(self, object_t) -> None:
        super().append(object_t)
        if len(self) > self.stackSize:
            self.popleft()

    def avg(self):
        return numpy.mean(self)

