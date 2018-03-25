import asyncio
import datetime
import multiprocessing
import os
import pathlib
import time
from concurrent.futures import ThreadPoolExecutor

import cv2
import psutil
import pyudev

from app.cam.PiCamera import PiCamera
from app.detector import Detector


class CV:

    def __init__(self):
        self.feed = PiCamera()

        self.isUpdated = False
        self.time = 0
        self.fps = 0
        self.imageBuf = None

        self.path = None

        self.detector = Detector()

        self.loop = asyncio.get_event_loop()
        self.pool = ThreadPoolExecutor(max_workers=multiprocessing.cpu_count())
        self.loop.run_in_executor(self.pool, self.process)
        self.loop.close()

    def get(self):
        while True:
            if self.isUpdated:
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n'
                       + self.imageBuf.tostring() + b'\r\n')
                self.isUpdated = False

    def process(self):
        while True:
            frame = self.feed.retrieve()
            self.count_fps()
            self.feed.auto_exposure(frame)

            birds = self.detector.search_on(frame)

            if len(birds) > 0:
                self.save(frame, birds)

            if not self.isUpdated:

                output = frame

                for (x, y, w, h) in birds:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                ret, self.imageBuf = cv2.imencode('*.jpg', output,
                                                  [cv2.IMWRITE_JPEG_QUALITY, 80])
                self.isUpdated = True

    def count_fps(self):
        if self.time == int(time.time()):
            self.fps += 1
        else:
            print('FPS: %i' % self.fps)
            self.time = int(time.time())
            self.fps = 0

    def save(self, frame, birds):
        removable = self.get_save_path()
        if removable is None: return
        if psutil.disk_usage(removable).free < 1024 * 1024: return
        now = datetime.datetime.now()
        folder = os.path.join(self.get_save_path(), now.strftime('%Y-%m-%d'), now.strftime('%H'))
        if not os.path.exists(folder):
            pathlib.Path(folder).mkdir(parents=True, exist_ok=True)
        file = now.strftime('%Y-%m-%d-%H-%M-%S-%f') + ".jpg"
        full_path = os.path.join(folder, file)
        print(full_path)
        cv2.imwrite(full_path, frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 100])
        for (x, y, w, h) in birds:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imwrite(os.path.join(folder, ''.join((file[:-4], '_a.jpg'))), frame,
                    [cv2.IMWRITE_JPEG_QUALITY, 50])

    def get_save_path(self):
        if self.path is not None:
            if os.path.exists(self.path):
                return self.path
        context = pyudev.Context()
        removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if
                     device.attributes.asstring('removable') == "1"]
        for device in removable:
            partitions = [device.device_node for device in
                          context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
            for p in psutil.disk_partitions():
                if p.device in partitions:
                    self.path = p.mountpoint
                    return self.path
