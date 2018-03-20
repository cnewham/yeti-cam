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
            return False  # motion disabled in configuration

        if self.last_motion_event is None or self.exceeds_motion_capture_delay():
            self.motion_events = 1
            self.last_motion_event = datetime.now()
            return True  # doesn't exceed motion capture delay
        elif self.motion_events + 1 <= config.get(constants.CONFIG_MOTION_CAPTURE_THRESHOLD):
            self.motion_events += 1
            self.last_motion_event = datetime.now()
            return True  # still within motion capture threshold
        else:
            logger.warning("Motion capture threshold exceeded")
            return False  # exceeds motion capture threshold

    def exceeds_motion_capture_delay(self):
        if self.last_motion_event is not None:
            delta_date = datetime.now() - timedelta(seconds=config.get(constants.CONFIG_MOTION_DELAY_SEC))
            return delta_date > self.last_motion_event
        else:
            return True


class SimpleGaussMotionDetector(picamera.array.PiRGBAnalysis):
    """
    Uses background subtraction using a gaussian average and background/foreground pixel weighting,
    and detects motion if there are any changes beyond the threshold value.
    Filters out significant changes due to lighting and camera image adjustments
    """
    def __init__(self, camera, handler, sensitivity, threshold, delay=3, percent_change_max=40):
        super(SimpleGaussMotionDetector, self).__init__(camera, size=(320, 240))
        self.handler = handler
        self.sensitivity = (sensitivity/255.0) ** 2 * 100
        self.threshold = (threshold/255.0) * 100
        self.alpha = (18/255.0) ** 3  # learning rate
        self.delay = delay
        self.last = datetime.now()
        self.background = None
        self.variance = None
        self.percent_change_max = percent_change_max

    def delayed(self):
        return (datetime.now() - timedelta(seconds=self.delay)) < self.last

    def analyse(self, a):
        if self.delayed():
            return

        try:
            logger.debug('Starting analysis')
            current = np.array(a, dtype=np.float64)

            if self.background is None:
                logger.debug('Building initial model...')
                self.background = current
                self.variance = np.full(current.shape, self.threshold, dtype=np.float64)
                logger.debug('Model complete')
                return

            logger.debug('Background subtraction...')
             #background subtraction
            delta = self.background - current
            logger.debug('Subtraction complete...')

            #pixel classification
            logger.debug('Classifying pixels...')
            foreground = (delta ** 2/self.variance).sum(axis=2)
            foreground[foreground < self.sensitivity] = 0 #background
            foreground[foreground >= self.sensitivity] = 255 #foreground

            logger.debug('Foreground Changed Pixels: %s' % np.count_nonzero(foreground))

            #foreground change percentage
            #pixel_changes = np.count_nonzero(foreground)
            #total_pixels = float(current.shape[0]*current.shape[1])
            #percent_change = (pixel_changes/total_pixels) * 100

            #logger.debug('Percent Change(changed %s, total %s: %s' % (pixel_changes, total_pixels, percent_change))
            #filter significant changes (i.e. lighting, camera adjustments)

            #if percent_change >= self.percent_change_max:
            #    logger.debug('Filtering out significant change (> %s%%) - %s%%' % (self.percent_change_max, percent_change))
            #    return

            #Model update
            logger.debug('Updating model...')
            self.background += delta * self.alpha
            self.variance += ((self.background - current) ** 2 - self.variance) * self.alpha
            np.clip(self.variance,0,self.threshold,out=self.variance)

            logger.debug('Model update complete...')
            logger.debug('Analysis complete')
            #self.last = datetime.now()
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


def get_filename(path, prefix, ext="jpg"):
    now = datetime.now()
    return "%s/%s%04d%02d%02d-%02d%02d%02d.%s" % ( path, prefix ,now.year, now.month, now.day, now.hour, now.minute, now.second, ext)