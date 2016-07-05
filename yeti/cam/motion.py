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
    """
    Calculates an average RGB value for each pixel, from a sample of images, and detects motion if there are any changes beyond
    the threshold value
    """
    def __init__(self, handler, sensitivity, threshold, delay=3, sample_size=10):
        self.handler = handler
        self.sensitivity = sensitivity
        self.threshold = threshold
        self.delay = delay
        self.last = datetime.now()
        self.background = None
        self.cache = []
        self.sample_size = sample_size

    def delayed(self):
        return (datetime.now() - timedelta(seconds=self.delay)) < self.last

    def analyse(self, a):
        if self.delayed():
            return        

        current = a.mean(axis=2) #calculate average RGB value for the current frame

        if not self.background: #check if we've built a big enough sample to average
            self.cache.append(current)
            if self.cache.count >= self.sample_size:
                sample = np.array(self.cache)
                self.background = sample.mean(axis=2) #average the background image for comparison to subsequent frames
                self.cache = []
            else:
                return               

        diff = abs(current - self.background)

        if (diff > self.threshold).sum() > self.sensitivity:
            self.handler.motion_detected()
            self.last = datetime.now()
            self.background = None


class SADMotionDetector(picamera.array.PiMotionAnalysis):
    """
    Sum of Absolute Differences - uses the built in picamera SAD calculation to analyze changes in pixels
    """
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
