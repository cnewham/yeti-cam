__author__ = 'chris'
import threading, time
import json
import pickledb
from yeti.common import constants
import Adafruit_DHT
import logging
logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
except RuntimeError:
    logger.exception("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

db = pickledb.load('db/sensors.db', True)

if not db.get(constants.SENSORS_TEMP):
    #default temp sensor locations
    logger.debug("adding default temp sensor config")
    db.dcreate(constants.SENSORS_TEMP)
    db.dadd(constants.SENSORS_TEMP, (constants.STATUS_INDOOR_TEMP, 4)) #{name : gpio}
    db.dadd(constants.SENSORS_TEMP, (constants.STATUS_OUTDOOR_TEMP, 17)) #{name : gpio}

if not db.get(constants.SENSORS_MOTION):
    #default motion sensor locations
    logger.debug("adding default motion sensor config")
    db.lcreate(constants.SENSORS_MOTION)

if not db.get(constants.SENSORS_READ_INTERVAL_SEC):
    db.set(constants.SENSORS_READ_INTERVAL_SEC, 30)


class GpioInputEvent(object):
    def __init__(self, channels):
        if not channels:
            return

        self.channels = channels or []

        logger.debug("channels: %s" % self.channels)
        GPIO.setup(channels, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        for channel in channels:
            logger.debug("adding event handler for channel %s" % channel)
            GPIO.add_event_detect(channel, GPIO.BOTH, callback=self._callback, bouncetime=200)

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
        super(Motion, self).__init__(db.lgetall(constants.SENSORS_MOTION))
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

class Temperature:
    readings = {}

    def __init__(self):
        self.pins = db.dgetall(constants.SENSORS_TEMP)
        logger.debug("Temperature: " + json.dumps(self.pins))
        self.t = threading.Thread(target=self.start)
        self.t.daemon = True
        self.t.start()

    def read(self, sensor = None):
        if sensor is None:
            return self.readings
        else:
            return self.readings[sensor]

    def start(self):
        logger.info("Starting temperature/humidity sensors")
        sensor = 22

        #Initialize readings with -1 value
        for name in db.dkeys(constants.SENSORS_TEMP):
            self.readings[name] = {}

        if self.readings is None:
            logger.warning("No temperature sensors have been initialized")
            return

        while True:
            for name, pin in db.dgetall(constants.SENSORS_TEMP).iteritems():
                try:
                    logger.debug("Getting temp reading for %s from pin %s" % (name, pin))

                    # Try to grab a sensor reading.  Use the read_retry method which will retry up
                    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
                    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

                    # Note that sometimes you won't get a reading and
                    # the results will be null (because Linux can't
                    # guarantee the timing of calls to read the sensor).
                    # If this happens try again!

                    if humidity is None or temperature is None:
                        logger.error("Failed to get temperature reading for %s, pin %s" % (name, pin))
                    else:
                        temperature = temperature * 9/5.0 + 32
                        logger.debug("Success: Temp %i Humidity %i" % (temperature, humidity))
                        self.readings[name] = {constants.STATUS_TEMP:temperature, constants.STATUS_HUMIDITY:humidity}
                except Exception:
                    logger.exception("An error occurred while attempting to read temperature sensors")

            time.sleep(db.get(constants.SENSORS_READ_INTERVAL_SEC))

    def stop(self):
        logger.info("Stopping...")
        self.t.join(3)

