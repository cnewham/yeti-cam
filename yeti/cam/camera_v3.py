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

class MotionEvents:
    def __init__(self):
        self.motion_events = 0
        self.last_motion_event = None

    def enabled(self):
        if not config.get(constants.CONFIG_MOTION_ENABLED):
            return False #motion disabled in configuration

        if self.last_motion_event is None or self.exceeds_motion_capture_delay():
            self.motion_events = 1
            self.last_motion_event = datetime.now()
            return True #doesn't exceed motion capture delay
        elif self.motion_events + 1 <= config.get(constants.CONFIG_MOTION_CAPTURE_THRESHOLD):
            self.motion_events += 1
            self.last_motion_event = datetime.now()
            return True #still within motion capture threshold
        else:
            return False #exceeds motion capture threshold

    def exceeds_motion_capture_delay(self):
        if self.last_motion_event is not None:
            delta_date = datetime.now() - timedelta(seconds=config.get(constants.CONFIG_MOTION_DELAY_SEC))
            return delta_date > self.last_motion_event
        else:
            return True

class MotionDetector(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, handler, sensitivity, threshold):
        super(MotionDetector, self).__init__(camera)
        self.handler = handler
        self.sensitivity = sensitivity
        self.threshold = threshold
        self.initializing = True

    def analyse(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)

        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion

        if (a > self.sensitivity).sum() > self.threshold:
            #skip the first motion detection while the camera may be still initializing
            if self.initializing:
                self.initializing = False
                return

            logger.debug("Motion Detected!")
            self.handler.trigger(constants.EVENT_MOTION)

class EventCaptureHandler:
    def __init__(self, callback=None):
        self.event = None
        self.callback = callback
        self.motion = MotionEvents()

    def trigger(self, event):
        if self.event:
            return False #already an event waiting to be processed

        if event == constants.EVENT_MOTION and self.motion.enabled():
            self.event = event
            return True
        else:
            self.event = event
            return True

    def capture(self, camera):
        with camera_lock: 
            filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), config.get(constants.CONFIG_IMAGE_PREFIX))
            camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
            camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)
            quality = config.get(constants.CONFIG_IMAGE_QUALITY)

            camera.exposure_mode = 'auto'
            camera.awb_mode = 'auto'
            camera.capture(filename, format="jpeg", quality=quality, use_video_port=True)

        if self.callback:
            self.callback(filename, event)

        self.event = None

    def start(self, callback):
        self.running = True
        with picamera.PiCamera() as camera:
            try:
                sensitivity = config.get(constants.CONFIG_MOTION_SENSITIVITY)
                threshold = config.get(constants.CONFIG_MOTION_THRESHOLD)

                camera.resolution = (config.get(constants.CONFIG_IMAGE_WIDTH), config.get(constants.CONFIG_IMAGE_HEIGHT))
                camera.framerate = 10
                camera.start_recording('/dev/null', format='h264', motion_output=MotionDetector(camera, self, sensitivity, threshold))
                
                while self.running:
                    if self.event:
                        self.capture(camera)

                    camera.wait_recording(1)
                    
            except Exception: 
                logger.exception("Camera failure has occurred. Restarting...")
            finally:
                camera.stop_recording()
                camera.close()
                self.running = False

    def stop(self):
        self.running = False

def get_filename(path, prefix):
    now = datetime.now()
    return "%s/%s%04d%02d%02d-%02d%02d%02d.jpg" % ( path, prefix ,now.year, now.month, now.day, now.hour, now.minute, now.second)



