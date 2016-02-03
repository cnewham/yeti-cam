__author__ = 'chris'

#!/usr/bin/python
#
#     Lightweight Motion Detection using python picamera libraries
#        based on code from raspberry pi forum by user utpalc
#        modified by Claude Pageau for this working example
#     ------------------------------------------------------------
# original code on github https://github.com/pageauc/picamera-motion

# This is sample code that can be used for further development

from datetime import datetime, timedelta
import time
from yeti.common import config, constants

import logging
logger = logging.getLogger(__name__)

logger.info("Starting camera")

import picamera
import picamera.array

#Constants
SECONDS2MICRO = 1000000  # Constant for converting Shutter Speed in Seconds to Microseconds

# User Customizable Settings
imageDir = config.get(constants.CONFIG_IMAGE_DIR)
imagePath = config.get(constants.CONFIG_IMAGE_DIR)
imageNamePrefix = config.get(constants.CONFIG_IMAGE_PREFIX)  # Prefix for all image file names. Eg front-

# Advanced Settings not normally changed
testWidth = 100
testHeight = 75

currentCount = 1000

def captureImage(filename):
    logger.info("Capturing Image - Working .....")
    with picamera.PiCamera() as camera:
        camera.resolution = (config.get(constants.CONFIG_IMAGE_WIDTH), config.get(constants.CONFIG_IMAGE_HEIGHT))
        camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
        camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        camera.capture(filename)
    logger.info("Capture Image - Captured %s" % filename)
    return filename

def takeMotionImage(width, height):
    with picamera.PiCamera() as camera:
        camera.resolution = (width, height)
        with picamera.array.PiRGBArray(camera) as stream:
            camera.exposure_mode = 'auto'
            camera.awb_mode = 'auto'
            camera.capture(stream, format='rgb')
            return stream.array

def scanMotion(sensitivity, threshold):
    width = testWidth
    height = testHeight
    data1 = takeMotionImage(width, height)
    while True:
        data2 = takeMotionImage(width, height)
        diffCount = 0L;
        for w in range(0, width):
            for h in range(0, height):
                # get the diff of the pixel. Conversion to int
                # is required to avoid unsigned short overflow.
                diff = abs(int(data1[h][w][1]) - int(data2[h][w][1]))
                if  diff > threshold:
                    diffCount += 1
            if diffCount > sensitivity:
                break; #break outer loop.
        if diffCount > sensitivity:
            return True
        else:
            time.sleep(1)

def getFileName(imagePath, imageNamePrefix):
    rightNow = datetime.now()
    return "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( imagePath, imageNamePrefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)

def capture_image():
    filename = getFileName(imagePath, imageNamePrefix)
    return captureImage(filename)

class MotionEvents:
    def __init__(self):
        self.motion_events = 0
        self.last_motion_event = None

    def enabled(self):
        #logger.debug("MotionEvents: last_motion_event: %s, motion_events: %s" % (self.last_motion_event, self.motion_events))

        if self.last_motion_event is None or self.exceeds_motion_capture_delay():
            self.motion_events = 1
            self.last_motion_event = datetime.now()
            #logger.debug("MotionsEvents: enabled - doesn't exceed motion capture delay")
            return True
        elif self.motion_events + 1 <= config.get(constants.CONFIG_MOTION_CAPTURE_THRESHOLD):
            self.motion_events += 1
            self.last_motion_event = datetime.now()
            #logger.debug("MotionsEvents: enabled - still within motion capture threshold")
            return True
        else:
            #logger.debug("MotionsEvents: disabled")
            return False

    def exceeds_motion_capture_delay(self):
        if self.last_motion_event is not None:
            delta_date = datetime.now() - timedelta(seconds=config.get(constants.CONFIG_MOTION_DELAY_SEC))
            #logger.debug("MotionEvents: delta_date: %s" % delta_date)
            return delta_date > self.last_motion_event
        else:
            return True
