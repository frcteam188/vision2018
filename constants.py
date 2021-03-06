import numpy as np

#IPs and Default Table
ServerIP = "10.1.88.2" #the roboRIO
MainTable = "SmartDashboard" #reduces java footprint since SmartDashboard
								#is already initialized
CubeStream = 0 #Bottom Camera
# TapeStream = 'http://localhost:1182/stream.mjpg' #Top Camera

MaxFPS = 8

CONTOUR_MIN = 300

CAMERA_WIDTH, CAMERA_HEIGHT = 1280, 720
WIDTH, HEIGHT = 640, 360
CAMERA_FOV = 53 # degrees
DEGREES_PER_PIXEL = CAMERA_FOV/WIDTH

#color ranges to filter
green_lower = np.array([50, 50, 50],np.uint8)
green_upper = np.array([100, 255, 255],np.uint8)

ANGLE_THRESHOLD = 20 #degrees
