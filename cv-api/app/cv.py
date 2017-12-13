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
        self.feed.set(cv2.CAP_PROP_FRAME_WIDTH,600)
        self.tmp = 't.jpg'
        self.isUpdated = False
        self.time = 0
        self.fps = 0
        
        self.loop = asyncio.get_event_loop()
        self.pool = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
        self.loop.run_in_executor(self.pool, self.process)
        self.loop.close()

    def get(self):
        while True:
            if self.isUpdated:
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' \
                   + open(self.tmp,'rb').read() + b'\r\n')
                self.isUpdated = False

    def return_frame():
        yield 

    def process(self):
        while True:
            if self.feed.grab() == True:
                
                if(self.time == int(time.time())):
                    self.fps += 1
                else:
                    print('FPS: real: %i: prop: %i' \
                          % (self.fps,self.feed.get(cv2.CAP_PROP_FPS)))
                    self.time = int(time.time())
                    self.fps=0
            
                rval, frame = self.feed.retrieve()
                if not self.isUpdated:
                    cv2.imwrite('t.jpg', frame)
                    self.isUpdated = True
        
                
