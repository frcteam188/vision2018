# import the necessary packages
from __future__ import print_function
from video import WebcamVideoStream
from video import FPS
import argparse
import imutils
import cv2
from tracker import detect_goals

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

print("[INFO] sampling THREADED frames from webcam...")
vs = WebcamVideoStream(src=0).start()

fps = FPS().start()
while True:
	frame = vs.read()
	detect_goals(frame, show_frame=(args["display"] > 0))
	fps.update()
 
# stop the timer and display FPS information
fps.stop()
 
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
