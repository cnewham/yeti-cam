from datetime import datetime, timedelta
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
    Uses background subtraction by calculating an average RGB value for each pixel over a series of frames (sample), 
    and detects motion if there are any changes beyond the threshold value.
    Filters out significant changes due to lighting and camera image adjustments
    """
    def __init__(self, camera, handler, sensitivity, threshold, delay=3, sample_size=10, percent_change_max=40):
        super(RGBMotionDetector, self).__init__(camera, size=(320, 240))
        self.handler = handler
        self.sensitivity = sensitivity
        self.threshold = threshold
        self.delay = delay
        self.last = datetime.now()
        self.reference = None
        self.cache = []
        self.sample_size = sample_size
        self.percent_change_max = percent_change_max

    def delayed(self):
        return (datetime.now() - timedelta(seconds=self.delay)) < self.last

    def analyse(self, a):
        if self.delayed():
            return

        try:
            #calculate average RGB value for the current frame
            current = a.mean(axis=2) 

            if self.reference is None:
                self.reference = current
                return

            #TODO: is it worth getting this average or just compare to a single frame and adjust the threshold?
            # if self.reference is None:
            #     self.cache.append(current)
            #     if len(self.cache) >= self.sample_size:
            #         #filter camera noise by averaging background image
            #         sample = np.array(self.cache)
            #         self.reference = sample.mean(axis=0)
            #         self.cache = []
            #     else:
            #         return

            #background subtraction
            diff = abs(self.reference - current)
            pixel_changes = (diff > self.threshold)

            total_changes = pixel_changes.sum()
            total_pixels = float(diff.shape[0]*diff.shape[1])
            percent_change = (total_changes/total_pixels) * 100

            logger.debug('Percent Change(changed %s, total %s: %s' % (total_changes, total_pixels, percent_change))
            #filter significant changes (i.e. lighting, camera adjustments)

            if percent_change >= self.percent_change_max:
                logger.debug('Filtering out significant change (> %s%%) - %s%%' % (self.percent_change_max, percent_change))
                return

            if percent_change <= 1:
                #logger.debug('Filtering out insignificant change (> %s%%) - %s%%' % (self.percent_change_max, percent_change))
                return

            #TODO: Compare motion area changes
            #motion_area = np.nonzero(pixel_changes)

            #print motion_area
            self.reference = current
            logger.debug('Motion Detected with value %s (threshold %s, sensitivity %s)' % (total_changes, self.threshold, self.sensitivity))
            self.handler.motion_detected()
            self.last = datetime.now()


        except Exception:
            logger.exception("Exception calculating motion")
            return

class SADMotionDetector(picamera.array.PiMotionAnalysis):
    """
    Sum of Absolute Differences - uses the built in picamera SAD calculation to analyze changes in pixels
    """
    def __init__(self, camera, handler, sensitivity, threshold, delay=3):
        super(SADMotionDetector, self).__init__(camera)
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
