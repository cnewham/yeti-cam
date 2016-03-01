#!/usr/bin/env python

__author__ = 'chris'
import threading
from datetime import datetime
import picamera
import picamera.array
import numpy as np
from yeti.common import config, constants

import logging
logger = logging.getLogger(__name__)

logger.info("Initializing camera")

camera_lock = threading.Lock()

initializing = True
motion_detected = False
capturing = False

class DetectMotion(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, sensitivity, threshold):
        super(DetectMotion, self).__init__(camera)
        self.sensitivity = sensitivity
        self.threshold = threshold

    def analyse(self, a):
        global motion_detected, initializing
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)

        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > self.sensitivity).sum() > self.threshold and not initializing:
            logger.debug("Motion Detected!")
            motion_detected = True

def get_filename(path, prefix):
    now = datetime.now()
    return "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( path, prefix ,now.year, now.month, now.day, now.hour, now.minute, now.second)

def capture_image():
    global capturing
    capturing = True
    filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), config.get(constants.CONFIG_IMAGE_PREFIX))

    with camera_lock:
        with picamera.PiCamera() as camera:
            camera.resolution = (config.get(constants.CONFIG_IMAGE_WIDTH), config.get(constants.CONFIG_IMAGE_HEIGHT))
            camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
            camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)
            quality = config.get(constants.CONFIG_IMAGE_QUALITY)

            camera.exposure_mode = 'auto'
            camera.awb_mode = 'auto'
            camera.capture(filename, format="jpeg", quality=quality)

    capturing = False
    return filename

def scan_motion(sensitivity, threshold):
    global motion_detected, initializing, capturing
    with camera_lock:
        with picamera.PiCamera() as camera:
            motion_detected = False
            initializing = True
            width = 640
            height = 480

            camera.resolution = (width, height)
            camera.framerate = 10
            camera.start_recording('/dev/null', format='h264', motion_output=DetectMotion(camera, sensitivity, threshold))

            while not motion_detected and not capturing:
                camera.wait_recording(1)
                initializing = False

    return motion_detected

