import os, time, datetime, pathlib
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import asyncio
import numpy
import pyudev
import psutil
from app import app
import cv2

class CV:

    def __init__(self):
        
        self.feed = cv2.VideoCapture(0)
        #self.feed.set(cv2.CAP_PROP_FRAME_WIDTH,800)
        #self.feed.set(cv2.CAP_PROP_FRAME_HEIGHT,600)
        self.feed.set(cv2.CAP_PROP_AUTO_EXPOSURE,0.25) # manual mode
        self.feed.set(cv2.CAP_PROP_EXPOSURE, 0.005)
        self.isUpdated = False
        self.time = 0
        self.fps = 0
        self.streamBuf = None

        self.path = None

        self.cascade = cv2.CascadeClassifier('app/cascade_114.xml')
        self.size = (200,200)

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

                exp = cv2.resize(frame,None,fx=0.25,fy=0.25, interpolation = cv2.INTER_LINEAR)

                self.autoExposure(cv2.cvtColor(exp, cv2.COLOR_BGR2YUV))

                #gray = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), \
                #                  None,fx=0.05, fy=0.05, interpolation = cv2.INTER_LINEAR)
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                birds = self.cascade.detectMultiScale(gray, 1.2, 2, \
                                                minSize=self.size)

                if len(birds) > 0:
                    self.save(frame, birds)
                
                if not self.isUpdated:

                    output = frame

                    for (x,y,w,h) in birds:
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

                    ret, self.imageBuf = cv2.imencode('*.jpg', \
                                output, \
                                [cv2.IMWRITE_JPEG_QUALITY, 80])
                    self.isUpdated = True

    def autoExposure(self, yuv_frame):
        self.skipCounter = self.skipCounter-1
        if (self.skipCounter < 1):
            lumaAvg = numpy.average(yuv_frame[:,:,0])
            #print(lumaAvg, self.getExposure())
            if (lumaAvg > 190) or (lumaAvg < 170):
                self.skipCounter = 2
                newExposure = 180*self.getExposure()/lumaAvg
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
            
    def save(self, frame, birds):
        now = datetime.datetime.now()
        folder = '{}/{}/{}'.format(self.getSavePath(), now.strftime('%Y-%m-%d'), now.strftime('%H'))
        if not os.path.exists(folder):
            pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
        file = now.strftime('%Y-%m-%d-%H-%M-%S-%f')
        print('{}/{}.jpg'.format(folder,file))
        cv2.imwrite('{}/{}.jpg'.format(folder,file),frame, \
                    [cv2.IMWRITE_JPEG_QUALITY, 100])
        for (x,y,w,h) in birds:
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.imwrite('{}/{}_a.jpg'.format(folder,file),frame, \
                    [cv2.IMWRITE_JPEG_QUALITY, 50])

    def getSavePath(self):
        if (self.path) is not None:
            if (os.path.exists(self.path)):
                return self.path
        context = pyudev.Context()
        removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if device.attributes.asstring('removable') == "1"]
        for device in removable:
            partitions = [device.device_node for device in context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
            for p in psutil.disk_partitions():
                if p.device in partitions:
                    self.path = p.mountpoint
                    return self.path
