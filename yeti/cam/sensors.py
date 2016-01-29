__author__ = 'chris'
import json
import pickledb
from yeti.common import log
from yeti.common import constants

db = pickledb.load('db/sensors.db', True)

#{name : gpio}
if not (db.get(constants.SENSORS_TEMP)):
    db.dcreate(constants.SENSORS_TEMP)
    db.dadd(constants.SENSORS_TEMP, (constants.STATUS_INDOOR_TEMP, 1))
    db.dadd(constants.SENSORS_TEMP, (constants.STATUS_OUTDOOR_TEMP, 2))

class Temperature:
    def __init__(self):
        self.sensors = db.dgetall(constants.SENSORS_TEMP)
        log.LogInfo(__name__, "Temperature: " + json.dumps(self.sensors))

    def read(self):
        return self.sensors
