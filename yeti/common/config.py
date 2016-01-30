__author__ = 'chris'
import pickledb
import json
from yeti.common import constants, log

db = pickledb.load('db/config.db', True)

if not db.get(constants.CONFIG_VERSION):
    db.set(constants.CONFIG_VERSION, 1)
if not db.get(constants.CONFIG_CHECK_UPDATES_MIN):
    db.set(constants.CONFIG_CHECK_UPDATES_MIN, 60)
if not db.get(constants.CONFIG_SERVER):
    db.set(constants.CONFIG_SERVER, "http://localhost:5000/api/")
if not db.get(constants.CONFIG_IMAGE_DIR):
    db.set(constants.CONFIG_IMAGE_DIR, "/home/pi/yeti/images")
if not db.get(constants.CONFIG_IMAGE_PREFIX):
    db.set(constants.CONFIG_IMAGE_PREFIX, "capture-")
if not db.get(constants.CONFIG_IMAGE_WIDTH):
    db.set(constants.CONFIG_IMAGE_WIDTH, 1980)
if not db.get(constants.CONFIG_IMAGE_HEIGHT):
    db.set(constants.CONFIG_IMAGE_HEIGHT, 1080)
if not db.get(constants.CONFIG_IMAGE_VFLIP):
    db.set(constants.CONFIG_IMAGE_VFLIP, False)
if not db.get(constants.CONFIG_IMAGE_HFLIP):
    db.set(constants.CONFIG_IMAGE_HFLIP, False)
if not db.get(constants.CONFIG_MOTION_THRESHOLD):
    db.set(constants.CONFIG_MOTION_THRESHOLD, 10)
if not db.get(constants.CONFIG_MOTION_SENSITIVITY):
    db.set(constants.CONFIG_MOTION_SENSITIVITY, 100)
if not db.get(constants.CONFIG_NIGHT_ISO):
    db.set(constants.CONFIG_NIGHT_ISO, 800)
if not db.get(constants.CONFIG_NIGHT_SHUTTER_SEC):
    db.set(constants.CONFIG_NIGHT_SHUTTER_SEC, 6)
if not db.get(constants.CONFIG_TIMER_INTERVAL_MIN):
    db.set(constants.CONFIG_TIMER_INTERVAL_MIN, 30)


def get(key = None):
    if key is None:
        with open('db/config.db', 'r') as configdb:
            configs = configdb.read()

        return json.loads(configs)
    else:
        return db.get(key)

def update(configs):
    log.LogInfo(__name__, "Updating configs")

    if not configs or configs is None:
        log.LogInfo(__name__, "No configs to update")
        return

    for key, value in configs.iteritems():
        db.set(key, value)


