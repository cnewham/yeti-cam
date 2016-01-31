__author__ = 'chris'
import threading, time
import json
import pickledb
from yeti.common import log
from yeti.common import constants
import Adafruit_DHT

db = pickledb.load('db/sensors.db', True)

#{name : gpio}
if not (db.get(constants.SENSORS_TEMP)):
    db.dcreate(constants.SENSORS_TEMP)
    db.dadd(constants.SENSORS_TEMP, (constants.STATUS_INDOOR_TEMP, 4))
    db.dadd(constants.SENSORS_TEMP, (constants.STATUS_OUTDOOR_TEMP, 17))

if not (db.get(constants.SENSORS_READ_INTERVAL_SEC)):
    db.set(constants.SENSORS_READ_INTERVAL_SEC, 30)


class Temperature:
    readings = {}

    def __init__(self):
        self.pins = db.dgetall(constants.SENSORS_TEMP)
        log.LogInfo(__name__, "Temperature: " + json.dumps(self.pins))
        self.t = threading.Thread(target=self.start)
        self.t.daemon = True
        #self.t.start()

    def read(self, sensor):
        return self.readings[sensor]

    def start(self):
        log.LogInfo(__name__, "Reading temperature/humidity")
        sensor = 22

        #Initialize readings with -1 value
        for name in db.dkeys(constants.SENSORS_TEMP):
            self.readings[name] = {constants.STATUS_TEMP:-1, constants.STATUS_HUMIDITY:-1}

        while True:
            for name, pin in db.dgetall(constants.SENSORS_TEMP).iteritems():
                log.LogVerbose(__name__, "Getting temp reading for %s from pin %s" % (name, pin))

                # Try to grab a sensor reading.  Use the read_retry method which will retry up
                # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
                humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

                # Un-comment the line below to convert the temperature to Fahrenheit.
                temperature = temperature * 9/5.0 + 32

                # Note that sometimes you won't get a reading and
                # the results will be null (because Linux can't
                # guarantee the timing of calls to read the sensor).
                # If this happens try again!

                if humidity is None or temperature is None:
                    log.LogError(__name__, "Failed to get temperature reading for %s" % name)
                else:
                    log.LogVerbose(__name__, "Success: Temp %s Humidity %s" % (temperature, humidity))
                    self.readings[name] = {constants.STATUS_TEMP:temperature, constants.STATUS_HUMIDITY:humidity}

            time.sleep(db.get(constants.SENSORS_READ_INTERVAL_SEC))

    def stop(self):
        log.LogInfo(__name__, "Stopping...")
        self.t.join(3)

