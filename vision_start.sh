#!/usr/bin/env bash

source /usr/local/bin/virtualenvwrapper.sh
workon cv
v4l2-ctl -c exposure_auto=1 -c exposure_absolute=10q
python /home/pi/Dev/vision2019/threading_track.py -d 1