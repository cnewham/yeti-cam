#!/usr/bin/env python

__author__ = 'chris'
import threading, time
from datetime import datetime, timedelta
import picamera
import picamera.array
import numpy as np
from yeti.common import config, constants

import logging
logger = logging.getLogger(__name__)

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

    def record(self):
        if not config.get(constants.CONFIG_MOTION_ENABLED):
            return False #motion disabled in configuration
            #TODO: implement logic to determine if a motion event should be recorded

    def exceeds_motion_capture_delay(self):
        if self.last_motion_event is not None:
            delta_date = datetime.now() - timedelta(seconds=config.get(constants.CONFIG_MOTION_DELAY_SEC))
            return delta_date > self.last_motion_event
        else:
            return True

class MotionDetector(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, handler, sensitivity, threshold, delay=3):
        super(MotionDetector, self).__init__(camera)
        self.handler = handler
        self.sensitivity = sensitivity
        self.threshold = threshold
        self.delay = delay
        self.last = datetime.now()

    def delayed(self):
        return (datetime.now() - timedelta(seconds=self.delay)) < self.last

    def analyse(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)

        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion

        if (a > self.sensitivity).sum() > self.threshold and not self.delayed():
            logger.debug("Motion Detected!")
            self.handler.trigger(constants.EVENT_MOTION)
            self.last = datetime.now()


class EventCaptureHandler:
    def __init__(self, callback=None):
        self.event = None
        self.stopping = False
        self.running = False
        self.callback = callback
        self.motion = MotionEvents()

    def trigger(self, event):
        logger.debug("Attempting to trigger %s event" % event)

        if self.event:
            logger.debug("Already an event waiting to be processed")
            return False

        if event == constants.EVENT_MOTION and not self.motion.enabled():
            logger.debug("Motion events disabled")
            return False

        logger.debug("Triggering %s event" % event)
        self.event = event
        return True

    def record(self, camera, seconds):
        logger.info("Recording %s event for %s seconds" % (self.event, seconds))

        filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), "recording-", "h264")
        camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
        camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)

        camera.exposure_mode = config.get(constants.CONFIG_IMAGE_EXPOSURE_MODE)
        camera.awb_mode = config.get(constants.CONFIG_IMAGE_AWB_MODE)

        camera.start_recording(filename, format='h264', splitter_port=2, resize=(640,480))
        camera.wait_recording(seconds, splitter_port=2)
        camera.stop_recording(splitter_port=2)

        if self.callback:
            self.callback(filename, self.event, constants.EVENT_TYPE_VIDEO)

        self.event = None


    def capture(self, camera):
        logger.info("Capture %s image" % self.event)
        with camera_lock: 
            filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), config.get(constants.CONFIG_IMAGE_PREFIX))
            camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
            camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)

            camera.exposure_mode = config.get(constants.CONFIG_IMAGE_EXPOSURE_MODE)
            camera.awb_mode = config.get(constants.CONFIG_IMAGE_AWB_MODE)

            camera.stop_recording()
            camera.capture(filename, format="jpeg", quality=config.get(constants.CONFIG_IMAGE_QUALITY))

        if self.callback:
            self.callback(filename, self.event, constants.EVENT_TYPE_IMAGE)

        self.event = None

    def start(self):
        if self.running:
            logger.warn("Camera already running")
            return

        logger.info("Starting camera")
        self.event = None
        self.running = True
        self.stopping = False
        with picamera.PiCamera() as camera:
            try:
                sensitivity = config.get(constants.CONFIG_MOTION_SENSITIVITY)
                threshold = config.get(constants.CONFIG_MOTION_THRESHOLD)

                camera.resolution = (config.get(constants.CONFIG_IMAGE_WIDTH), config.get(constants.CONFIG_IMAGE_HEIGHT))
                camera.framerate = 10

                logger.info("Starting capture")
                camera.start_recording('/dev/null', format='h264', motion_output=MotionDetector(camera, self, sensitivity, threshold))

                while not self.stopping:
                    logger.debug("checking for events")

                    if self.event:
                        self.capture(camera)

                        #self.record(camera, 5)
                        logger.info("Continuing capture")
                        camera.start_recording('/dev/null', format='h264', motion_output=MotionDetector(camera, self, sensitivity, threshold))

                    time.sleep(1)

            except Exception:
                logger.exception("Camera failure has occurred")
            finally:
                logger.info("Stopping camera")
                camera.close()
                self.running = False

    def stop(self):
        if self.running:
            self.stopping = True

            while self.running:
                time.sleep(.5)

    def restart(self):
        logger.info("Restarting camera")
        self.stop()
        self.start()

def get_filename(path, prefix, ext="jpg"):
    now = datetime.now()
    return "%s/%s%04d%02d%02d-%02d%02d%02d.%s" % ( path, prefix ,now.year, now.month, now.day, now.hour, now.minute, now.second, ext)



