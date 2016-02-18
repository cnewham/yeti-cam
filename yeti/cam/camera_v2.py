#!/usr/bin/env python

__author__ = 'chris'
from datetime import datetime
import picamera
import picamera.array
import numpy as np
from yeti.common import config, constants

import logging
logger = logging.getLogger(__name__)

motion_detected = False
motion_starting = True

imageDir = config.get(constants.CONFIG_IMAGE_DIR)
imagePath = config.get(constants.CONFIG_IMAGE_DIR)
imageNamePrefix = config.get(constants.CONFIG_IMAGE_PREFIX)  # Prefix for all image file names. Eg front-

class DetectMotion(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, sensitivity, threshold):
        super(DetectMotion, self).__init__(camera)
        self.sensitivity = sensitivity
        self.threshold = threshold

    def analyse(self, a):
        global motion_detected, motion_starting
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > self.sensitivity).sum() > self.threshold and not motion_starting:
            logger.debug("Motion Detected!")
            motion_detected = True

def getFileName(imagePath, imageNamePrefix):
    now = datetime.now()
    return "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( imagePath, imageNamePrefix ,now.year, now.month, now.day, now.hour, now.minute, now.second)

def capture_image():
    filename = getFileName(imagePath, imageNamePrefix)

    with picamera.PiCamera() as camera:
        camera.resolution = (config.get(constants.CONFIG_IMAGE_WIDTH), config.get(constants.CONFIG_IMAGE_HEIGHT))
        camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
        camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)
        quality = config.get(constants.CONFIG_IMAGE_QUALITY)

        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        camera.capture(filename, format="jpeg", quality=quality, splitter_port=1)

    return filename

def scanMotion(sensitivity, threshold):
    global motion_detected, motion_starting
    with picamera.PiCamera() as camera:
        motion_detected = False
        motion_starting = True

        camera.resolution = (640, 480)
        camera.framerate = 10
        camera.start_recording('/dev/null', format='h264', motion_output=DetectMotion(camera, sensitivity, threshold))

        while not motion_detected:
            camera.wait_recording(1)
            motion_starting = False

        camera.stop_recording()
        return True

