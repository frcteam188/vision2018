from __future__ import print_function

import numpy as np
import cv2
import logging
import constants
import imutils
import math
import time
from networktables import NetworkTables
from multiprocessing.pool import ThreadPool
from collections import deque
from common import clock, draw_str, StatValue

from tracker import detect_goals

logging.basicConfig(level=logging.DEBUG)
camera = cv2.VideoCapture(0)

class DummyTask:
    def __init__(self, data):
        self.data = data
    def ready(self):
        return True
    def get(self):
        return self.data

if __name__ == '__main__':
    import sys

    print(__doc__)

    try:
        fn = sys.argv[1]
    except:
        fn = 0
    
    def process_frame(frame, t0):
        frame = detect_goals(frame)
        return frame, t0

    threadn = cv2.getNumberOfCPUs()
    pool = ThreadPool(processes = threadn)
    pending = deque()

    threaded_mode = True

    latency = StatValue()
    frame_interval = StatValue()
    last_frame_time = clock()
    while True:
        while len(pending) > 0 and pending[0].ready():
            res, t0 = pending.popleft().get()
            latency.update(clock() - t0)
            draw_str(res, (20, 20), "threaded      :  " +             str(threaded_mode))
            draw_str(res, (20, 40), "latency        :  %.1f ms" %     (latency.value*1000))
            draw_str(res, (20, 60), "frame interval :  %.1f ms" % (frame_interval.value*1000))
            cv2.imshow('threaded video', res)
        if len(pending) < threadn:
            ret, frame = camera.read()
            if frame is not None:
                t = clock() 
                frame_interval.update(t - last_frame_time)
                last_frame_time = t
                if threaded_mode:
                    task = pool.apply_async(process_frame, (frame.copy(), t))
                else:
                    task = DummyTask(process_frame(frame, t))
                pending.append(task)
        ch = cv2.waitKey(1)
        if ch == ord(' '):
            threaded_mode = not threaded_mode
        if ch == 27:
            break
    cv2.destroyAllWindows()
