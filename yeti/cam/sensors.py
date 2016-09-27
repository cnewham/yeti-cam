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
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
except RuntimeError:
    logger.error("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

db = pickledb.load('db/sensors.db', True)

if not db.get(constants.SENSORS_TEMP):
    #default temp sensor locations
    db.dcreate(constants.SENSORS_TEMP)
    db.dadd(constants.SENSORS_TEMP, (constants.STATUS_INDOOR_TEMP, 4)) #{name : gpio}
    db.dadd(constants.SENSORS_TEMP, (constants.STATUS_OUTDOOR_TEMP, 17)) #{name : gpio}

if not db.get(constants.SENSORS_MOTION):
    #default motion sensor locations
    db.lcreate(constants.SENSORS_MOTION)
    db.ladd(constants.SENSORS_MOTION, 19)

if not db.get(constants.SENSORS_READ_INTERVAL_SEC):
    db.set(constants.SENSORS_READ_INTERVAL_SEC, 30)


class ThreadedGpioInput:
    def __init__(self, channels):
        if not channels:
            return

        GPIO.setup(channels, GPIO.IN)

        for channel in channels:
            GPIO.add_event_detect(channel, GPIO.RISING, callback=self.activated, bouncetime=200)
            GPIO.add_event_detect(channel, GPIO.FALLING, callback=self.deactivated, bouncetime=200)

    def activated(self, channel):
        #overridable: called when a channel goes active
        pass

    def deactivated(self, channel):
        #overridable: called when a channel goes inactive
        pass
                
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop()
        GPIO.cleanup(self.channels)

class Motion(ThreadedGpioInput):
    def __init__(self, callback):
        super(Motion, self).__init__(db.lgetall(constants.SENSORS_MOTION))
        self.callback = callback

    def activated(self, channel):
        logger.debug("Motion Channel %s has been activated" % channel)
        callback(True)

    def deactivated(self, channel):
        logger.debug("Motion Channel %s has been deactivated" % channel)
        callback(False)

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

