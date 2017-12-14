import os, time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import asyncio
from app import app
import cv2

class CV:

    def __init__(self):
        self.feed = cv2.VideoCapture(0)
        self.feed.set(cv2.CAP_PROP_FRAME_WIDTH,800)
        self.feed.set(cv2.CAP_PROP_FRAME_HEIGHT,600)
        self.isUpdated = False
        self.time = 0
        self.fps = 0
        self.streamBuf = None
        
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

    def return_frame():
        yield 

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
                if not self.isUpdated:
                    ret, self.imageBuf = cv2.imencode('*.jpg', frame)
                    self.isUpdated = True
        
                
