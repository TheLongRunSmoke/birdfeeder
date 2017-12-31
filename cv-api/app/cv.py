import os, time, timeit
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
        self.feed.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.25) # manual mode
        self.feed.set(cv2.CAP_PROP_EXPOSURE, 0.005)
        self.isUpdated = False
        self.time = 0
        self.fps = 0
        self.streamBuf = None

        self.substractor = cv2.bgsegm.createBackgroundSubtractorCNT(minPixelStability = 5,
                              useHistory = True,
                              maxPixelStability = 5*60,
                              isParallel = False)
        self.history = 100

        self.skipCounter=0
        
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

                self.countFPS()
            
                rval, frame = self.feed.retrieve()
                
                self.autoExposure(cv2.cvtColor(frame, cv2.COLOR_BGR2YUV))

                gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), \
                                  None,fx=0.2, fy=0.2, interpolation = cv2.INTER_LINEAR)                  

                mask = self.substractor.apply(gray)
                mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                mask = cv2.resize(mask, frame.shape[1::-1])
                
                if not self.isUpdated:
                    ret, self.imageBuf = cv2.imencode('*.jpg', \
                                        numpy.concatenate((frame, frame & mask), axis=0))
                    self.isUpdated = True

    #@timeit
    def autoExposure(self, yuv_frame):
        self.skipCounter = self.skipCounter-1
        if (self.skipCounter < 1):
            lumaAvg = numpy.average(yuv_frame[:,:,0])
            print(lumaAvg, self.getExposure())
            if (lumaAvg > 190) or (lumaAvg < 160):
                self.skipCounter = 2
                newExposure = 175*self.getExposure()/lumaAvg
                if (newExposure < 1):
                    print("newExposure: %f" % newExposure)
                    self.feed.set(cv2.CAP_PROP_EXPOSURE, newExposure)

    def getExposure(self):
        exp = self.feed.get(cv2.CAP_PROP_EXPOSURE)
        return exp

    def countFPS(self):
        if(self.time == int(time.time())):
            self.fps += 1
        else:
            print('FPS: %i' % (self.fps))
            self.time = int(time.time())
            self.fps=0

    def timeit(method):
        def timed(*args, **kw):
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()
            if 'log_time' in kw:
                name = kw.get('log_name', method.__name__.upper())
                kw['log_time'][name] = int((te - ts) * 1000)
            else:
                print('%r  %2.2f ms' % \
                      (method.__name__, (te - ts) * 1000))
            return result
        return timed
