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
        self.feed.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.25) # manual mode
        self.feed.set(cv2.CAP_PROP_EXPOSURE, 0.005)
        self.isUpdated = False
        self.time = 0
        self.fps = 1
        self.streamBuf = None

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
                                  None,fx=0.4, fy=0.4, interpolation = cv2.INTER_CUBIC)                  

                img_dft = cv2.dft(numpy.float32(gray),flags=cv2.DFT_COMPLEX_OUTPUT)
                magnitude, angle = cv2.cartToPolar(img_dft[:, :, 0], img_dft[:, :, 1])
                log_ampl = numpy.log10(magnitude.clip(min=1e-9))
                log_ampl_blur = cv2.blur(log_ampl, (3, 3))
                magn = numpy.exp(log_ampl-log_ampl_blur)
                img_dft[:, :, 0], img_dft[:, :, 1] = cv2.polarToCart(magn, angle)
                img_combined = cv2.idft(img_dft)
                sal, _ = cv2.cartToPolar(img_combined[:, :, 0], img_combined[:, :, 1])

                sal = cv2.GaussianBlur(sal,(5,5),sigmaX=8, sigmaY=0)

                sal = sal**2
                sal = 256*numpy.float32(sal)/numpy.max(sal)
                sal = cv2.resize(sal, frame.shape[1::-1])

                colorSal = cv2.cvtColor(numpy.array(sal, dtype=numpy.uint8),cv2.COLOR_GRAY2BGR)
                
                if not self.isUpdated:
                    #ret, self.imageBuf = cv2.imencode('*.jpg', colorSal)
                    ret, self.imageBuf = cv2.imencode('*.jpg', \
                                        numpy.concatenate((frame, colorSal), axis=0))
                    self.isUpdated = True

    def autoExposure(self, yuv_frame):
        self.skipCounter = self.skipCounter-1
        if (self.skipCounter < 1):
            lumaAvg = numpy.average(yuv_frame[:,:,0])
            print(lumaAvg, self.getExposure())
            if (lumaAvg > 190) or (lumaAvg < 160):
                self.skipCounter = 2
                newExposure = 175*self.getExposure()/lumaAvg
                print("newExposure: %f" % newExposure)
                if (newExposure < 1):
                    self.feed.set(cv2.CAP_PROP_EXPOSURE, newExposure)

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

    def countFPS(self):
        if(self.time == int(time.time())):
            self.fps += 1
        else:
            print('FPS: %i' % (self.fps))
            self.time = int(time.time())
            self.fps=1
