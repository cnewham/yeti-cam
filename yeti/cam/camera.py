__author__ = 'chris'

#!/usr/bin/python
#
#     Lightweight Motion Detection using python picamera libraries
#        based on code from raspberry pi forum by user utpalc
#        modified by Claude Pageau for this working example
#     ------------------------------------------------------------
# original code on github https://github.com/pageauc/picamera-motion

# This is sample code that can be used for further development

verbose = True
if verbose:
    print "Loading python libraries ....."
else:
    print "verbose output has been disabled verbose=False"

import datetime
import time
import os
from fractions import Fraction

from yeti.common import config, constants

import picamera
import picamera.array

#Constants
SECONDS2MICRO = 1000000  # Constant for converting Shutter Speed in Seconds to Microseconds

# User Customizable Settings
imageDir = config.get(constants.CONFIG_IMAGE_DIR)
imagePath = config.get(constants.CONFIG_IMAGE_DIR)
imageNamePrefix = config.get(constants.CONFIG_IMAGE_PREFIX)  # Prefix for all image file names. Eg front-
imageWidth = config.get(constants.CONFIG_IMAGE_WIDTH)
imageHeight = config.get(constants.CONFIG_IMAGE_HEIGHT)
imageVFlip = config.get(constants.CONFIG_IMAGE_VFLIP)   # Flip image Vertically
imageHFlip = config.get(constants.CONFIG_IMAGE_HFLIP)   # Flip image Horizontally
imagePreview = False

numberSequence = False

threshold = config.get(constants.CONFIG_MOTION_THRESHOLD)  # How Much pixel changes
sensitivity = config.get(constants.CONFIG_MOTION_SENSITIVITY)  # How many pixels change
motionISO = config.get(constants.CONFIG_NIGHT_ISO)
motionShutSpeed = config.get(constants.CONFIG_NIGHT_SHUTTER_SEC) * SECONDS2MICRO  # seconds times conversion to microseconds constant

# Advanced Settings not normally changed
testWidth = 100
testHeight = 75

currentCount = 1000
motionCount = 0

def captureImage(imageWidth, imageHeight, filename):
    if verbose:
        print "takeDayImage - Working ....."
    with picamera.PiCamera() as camera:
        camera.resolution = (imageWidth, imageHeight)
        if imagePreview:
            camera.start_preview()
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        camera.capture(filename)
    if verbose:
        print "takeDayImage - Captured %s" % (filename)
    return filename

def takeMotionImage(width, height, daymode):
    with picamera.PiCamera() as camera:
        camera.resolution = (width, height)
        with picamera.array.PiRGBArray(camera) as stream:
            if daymode:
                camera.exposure_mode = 'auto'
                camera.awb_mode = 'auto'
            else:
                # Take Low Light image
                # Set a framerate of 1/6 fps, then set shutter
                # speed to 6s and ISO to 800
                camera.framerate = Fraction(1, 6)
                camera.shutter_speed = motionShutSpeed
                camera.exposure_mode = 'off'
                camera.iso = motionISO
                # Give the camera a good long time to measure AWB
                # (you may wish to use fixed AWB instead)
                time.sleep( 10 )
            camera.capture(stream, format='rgb')
            return stream.array

def scanMotion(width, height, daymode):
    motionFound = False
    data1 = takeMotionImage(width, height, daymode)
    while not motionFound:
        data2 = takeMotionImage(width, height, daymode)
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
            motionFound = True
        else:
            data2 = data1
            time.sleep(1)

    return motionFound

def getFileName(imagePath, imageNamePrefix, currentCount):
    rightNow = datetime.datetime.now()
    if numberSequence :
        filename = imagePath + "/" + imageNamePrefix + str(currentCount) + ".jpg"
    else:
        filename = "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( imagePath, imageNamePrefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second)
    return filename

def motion_detect():
    print "Scanning for Motion threshold=%i sensitivity=%i ......"  % (threshold, sensitivity)
    isDay = True
    while True:
        if scanMotion(testWidth, testHeight, isDay):
            filename = getFileName(imagePath, imageNamePrefix, currentCount)
            captureImage( imageWidth, imageHeight, filename )



