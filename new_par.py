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
NetworkTables.initialize(server=constants.ServerIP)
Table = NetworkTables.getTable(constants.MainTable)

cap = cv2.VideoCapture(0)

class DummyTask:
    def __init__(self, data):
        self.data = data
    def ready(self):
        return True
    def get(self):
        return self.data

def process_frame(frame, t0):
	frame = detect_goals(frame)
	return frame, t0

def trackGoals():
	print('tracking')

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
			ret, frame = cap.read()
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
    
def detect_goals(frame):
	before = time.time()
	frame = cv2.resize(frame, (constants.WIDTH, constants.HEIGHT))

	#sharpen and refine image
	hsv = frame
	
	hsv = cv2.erode(hsv, None, iterations=2)
	hsv = cv2.dilate(hsv, None, iterations=2)
	hsv = cv2.GaussianBlur(hsv, (3, 3), 1)

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	#filter anything based on color
	green_range = cv2.inRange(hsv, constants.green_lower, constants.green_upper)
	# cv2.imshow('FILTER', green_range)
	# print_latency(before)
	try:
		b, contours, _ = cv2.findContours(green_range, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		rects = [np.int0(cv2.boxPoints(cv2.minAreaRect(contour))) for contour in contours if cv2.contourArea(contour) > 150]
		matches = find_goals(frame, rects)
		if matches is not None:
			write_angles(frame, matches)
		cv2.drawContours(frame,rects,-1,(0,0,255),2)
		
		# #send data to table
		# Table.putNumber("DistanceToCube", DistanceToCube)
		# Table.putNumber("PixelsToCube", PixelsToCube)
		# Table.putNumberArray("X, Y, W, H", CubeData)
		# Table.putNumber("CenterOfCube", CenterOfCube)
		# Table.putNumber("AngleToCube", AngleToCube)
		Table.putBoolean("ContoursFound", True)

	except IndexError:
		Table.putBoolean("ContoursFound", False)
	# print_latency(before)
	cv2.imshow("Frame", frame)
	return frame

def write_angles(frame, matches):
    for s1, s2 in matches:
        match_center = (s1[3][0] + s2[0][0]) / 2
        camera_center = constants.WIDTH/2
        angle_to_match = (match_center-camera_center) * constants.DEGREES_PER_PIXEL
        cv2.putText(frame, "%.2f"%angle_to_match, (int(match_center), s1[3][1]), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))

def find_goals(frame, rects):
    if len(rects) < 2:
        return None
    matches = []
    matched = {}
    rects = [sorted(rect, key=lambda x: x[0]) for rect in rects]
    rects = sorted(rects,  key=lambda x: x[0][0])
    for s1 in rects:
        # s1 = sorted(r1, key=lambda x: x[0])
        a1 = get_angle(s1)
        for s2 in rects:
            if s2 is not s1:
                # s2 = sorted(r2, key=lambda x: x[0])
                a2 = get_angle(s2)
                # print('here')
                # check s1 to the left of s2, and both at same height
                if (s1[0][0] < s2[0][0] and abs(s1[3][1] - s2[0][1]) < 50):
                    # check a1 reflects a2 along the vertical (within a threshold)
                    if a2 > a1 and a1 != 0 and a2/a1 < 0 and abs(a2 + a1) < constants.ANGLE_THRESHOLD:
                        if str(s1) not in matched and str(s2) not in matched:
                            match = (s1, s2)
                            matched[str(s1)] = match
                            matched[str(s2)] = match
                            matches.append(match)
                            cv2.line(frame, tuple(s1[3]), tuple(s2[0]), (0, 255, 0), 3)
    return matches
            # print(angle, angle+90%360)
    return frame

def get_angle(rect):
    p1, p2 = rect[0], rect[1]
    opposite = p2[0] - p1[0]
    adjacent = p2[1] - p1[1]
    angle = (math.atan(opposite/adjacent) * 180)/math.pi
    return angle

def print_latency(before):
    latency = time.time() - before
    fps = (1/latency)
    fps_str = '%.2f'%fps
    print('FPS:', fps_str, 'Latency:', latency)
    
if __name__ == '__main__':
    trackGoals()
    # detect_goals(cv2.imread('vision_sample.png'))
    # cv2.waitKey(0)
