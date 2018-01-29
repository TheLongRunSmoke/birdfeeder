import os, time, datetime, pathlib
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import asyncio
import numpy
from app import app
import cv2

class CV:

    def __init__(self):

        self.PATH = '/home/pi/Desktop/captures/'
        
        self.feed = cv2.VideoCapture(0)
        self.feed.set(cv2.CAP_PROP_FRAME_WIDTH,800)
        self.feed.set(cv2.CAP_PROP_FRAME_HEIGHT,600)
        self.feed.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.25) # manual mode
        self.feed.set(cv2.CAP_PROP_EXPOSURE, 0.005)
        self.isUpdated = False
        self.time = 0
        self.fps = 0
        self.streamBuf = None

        self.lastSharpness = 0
        
        self.substractor = cv2.bgsegm.createBackgroundSubtractorCNT(minPixelStability = 5,
                             useHistory = False,
                             maxPixelStability = 5*60,
                             isParallel = False)

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

                luma = self.autoExposure(cv2.cvtColor(frame, cv2.COLOR_BGR2YUV))

                gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), \
                                  None,fx=0.05, fy=0.05, interpolation = cv2.INTER_LINEAR)                  
                mask = self.substractor.apply(gray)
                
                if self.isBird(mask):
                        sharpness = self.checkAndSave(frame)
                
                if not self.isUpdated:

                    output = frame

                    text = "Nothing"
                    if self.isBird(mask):
                        text = "Bird presence"
                        cv2.putText(output, str(sharpness), (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2,cv2.LINE_AA)
                    cv2.putText(output, text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2,cv2.LINE_AA)
                    

                    ret, self.imageBuf = cv2.imencode('*.jpg', \
                                output, \
                                [cv2.IMWRITE_JPEG_QUALITY, 80])
                    self.isUpdated = True

    def autoExposure(self, yuv_frame):
        self.skipCounter = self.skipCounter-1
        if (self.skipCounter < 1):
            lumaAvg = numpy.average(yuv_frame[:,:,0])
            #print(lumaAvg, self.getExposure())
            if (lumaAvg > 190) or (lumaAvg < 165):
                self.skipCounter = 2
                newExposure = 175*self.getExposure()/lumaAvg
                if (newExposure < 1):
                    #print("newExposure: %f" % newExposure)
                    self.feed.set(cv2.CAP_PROP_EXPOSURE, newExposure)
            return lumaAvg
        return 0

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

    def isBird(self, mask):
        height, width = mask.shape
        maximum=height*width*255
        maskSum = numpy.sum(mask)
        if not ((maskSum < maximum*0.1) or (maskSum > maximum*0.6)):
            return True
        return False
            

    def checkAndSave(self, frame):
        # check sharpness
        sharpness = cv2.Laplacian(frame, cv2.CV_64F).var()
        if sharpness > self.lastSharpness:
            now = datetime.datetime.now()
            folder = '{}{}'.format(self.PATH, now.strftime('%Y-%m-%d'))
            if not os.path.exists(folder):
                pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
            file = now.strftime('%H-%M-%S-%f')
            print('{}/{}.jpg'.format(folder,file))
            cv2.imwrite('{}/{}.jpg'.format(folder,file),frame, \
                        [cv2.IMWRITE_JPEG_QUALITY, 80])
        self.lastSharpness = sharpness
        return self.lastSharpness
            
