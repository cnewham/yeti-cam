__author__ = 'chris'

#!/usr/bin/python
#
#     Lightweight Motion Detection using python picamera libraries
#        based on code from raspberry pi forum by user utpalc
#        modified by Claude Pageau for this working example
#     ------------------------------------------------------------
# original code on github https://github.com/pageauc/picamera-motion

# This is sample code that can be used for further development

log.LogInfo(__name__, "Starting camera")

import datetime
import time

from yeti.common import config, constants, log

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
    log.LogInfo(__name__, "Capturing Image - Working .....")
    with picamera.PiCamera() as camera:
        camera.resolution = (config.get(constants.CONFIG_IMAGE_WIDTH), config.get(constants.CONFIG_IMAGE_HEIGHT))
        camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
        camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        camera.capture(filename)
    log.LogInfo(__name__, "takeDayImage - Captured %s" % filename)
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
    rightNow = datetime.datetime.now()
    return "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( imagePath, imageNamePrefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)

def capture_image():
    filename = getFileName(imagePath, imageNamePrefix)
    return captureImage(filename)


