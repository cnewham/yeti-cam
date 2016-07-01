import picamera
import picamera.array
import numpy as np
from yeti.common import config, constants

import logging
logger = logging.getLogger(__name__)

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
            logger.warning("Motion capture threshold exceeded")
            return False #exceeds motion capture threshold

    def exceeds_motion_capture_delay(self):
        if self.last_motion_event is not None:
            delta_date = datetime.now() - timedelta(seconds=config.get(constants.CONFIG_MOTION_DELAY_SEC))
            return delta_date > self.last_motion_event
        else:
            return True

class RGBMotionDetector(picamera.array.PiRGBAnalysis):
    def __init__(self, handler, sensitivity, threshold, delay=3):
        self.handler = handler
        self.sensitivity = sensitivity
        self.threshold = threshold
        self.delay = delay
        self.last = datetime.now()

    def delayed(self):
        return (datetime.now() - timedelta(seconds=self.delay)) < self.last

    def analyse(self, array):
        #TODO: Motion detection analysis here

        self.handler.motion_detected()
        self.last = datetime.now()


class VectorMotionDetector(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, handler, sensitivity, threshold, delay=3):
        super(VectorMotionDetector, self).__init__(camera)
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

            self.handler.motion_detected()
            self.last = datetime.now()
