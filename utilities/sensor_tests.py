__author__ = 'chris'
import sys, signal, time
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG,
                    format="%(name)-12s: %(levelname)-8s %(message)s")

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
except RuntimeError:
    logger.exception("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")


class GpioInputEvent(object):
    def __init__(self, channels, bouncetime=200):
        if not channels:
            return

        self.channels = channels or []

        logger.debug("channels: %s" % self.channels)
        GPIO.setup(channels, GPIO.IN)

        for channel in channels:
            logger.debug("adding event handler for channel %s" % channel)
            GPIO.add_event_detect(channel, GPIO.BOTH, callback=self._callback, bouncetime=bouncetime)

    def _callback(self, channel):
        if GPIO.input(channel):
            self.activated(channel)
        else:
            self.deactivated(channel)

    def activated(self, channel):
        #overridable: called when a channel goes active
        pass

    def deactivated(self, channel):
        #overridable: called when a channel goes inactive
        pass
                
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        logger.debug("Cleaning up channels")
        GPIO.cleanup(self.channels)

class Motion(GpioInputEvent):
    def __init__(self, callback):
        super(Motion, self).__init__([4,17])
        self.callback = callback
        self.motion_detected = {}

    def activated(self, channel):
        logger.debug("Motion Channel %s has been activated" % channel)

        if any(self.motion_detected.values()):
            self.motion_detected[channel] = True
            return
        else: 
            self.motion_detected[channel] = True
            if self.callback:
                self.callback(True) #send callback the first time a channel starts detecting motion

    def deactivated(self, channel):
        logger.debug("Motion Channel %s has been deactivated" % channel)

        self.motion_detected[channel] = False

        if not any(self.motion_detected.values()):
            if self.callback:
                self.callback(False) #send callback after the last channel stops detecting motion


class RF433(GpioInputEvent):
    def __init__(self):
        super(RF433, self).__init__([22])
        self.timer = time.time()

    def elapse(self):
        delta = time.time() - self.timer
        self.timer = time.time()
        return delta

    def activated(self, channel):
        print("ON\n")

    def deactivated(self, channel):
        print("OFF\n")


def callback(channel):
    logger.debug("callback called for channel %s" % channel)

#with Motion(callback) as motion:
#    while True:
#        time.sleep(1)

def signal_handler(signal, frame):
    logger.warning("Stop signal detected...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)