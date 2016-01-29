__author__ = 'chris'
from yeti.common import constants
import pickledb

#Configuration
db = pickledb.load('db/cam.db', True)

if not db.get(constants.CONFIG):
    db.dcreate(constants.CONFIG)
    db.dadd(constants.CONFIG, (constants.CONFIG_VERSION, 1))

if not (db.get(constants.CONFIG_SENSORS)):
    db.dcreate(constants.CONFIG_SENSORS)
    db.dadd(constants.CONFIG_SENSORS, (constants.STATUS_INDOOR_TEMP, 1))
    db.dadd(constants.CONFIG_SENSORS, (constants.STATUS_OUTDOOR_TEMP, 2))


#Application starts here, this is where it all goes down
import sensors
import http
import camera

temp = sensors.Temperature()
print temp.read()

