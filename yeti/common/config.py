__author__ = 'chris'
import pickledb
import json
from yeti.common import constants
import logging
logger = logging.getLogger(__name__)

db = pickledb.load('db/config.db', True)

#server/config
if not db.get(constants.CONFIG_VERSION):
    db.set(constants.CONFIG_VERSION, 0)
if not db.get(constants.CONFIG_CHECK_INTERVAL_MIN):
    db.set(constants.CONFIG_CHECK_INTERVAL_MIN, 60)
if not db.get(constants.CONFIG_SERVER):
    db.set(constants.CONFIG_SERVER, "http://localhost:5000/api/")

#image
if not db.get(constants.CONFIG_IMAGE_DIR):
    db.set(constants.CONFIG_IMAGE_DIR, "/home/yeti/cam/images")
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

#motion
if not db.get(constants.CONFIG_MOTION_ENABLED):
    db.set(constants.CONFIG_MOTION_ENABLED, True)
if not db.get(constants.CONFIG_MOTION_THRESHOLD):
    db.set(constants.CONFIG_MOTION_THRESHOLD, 10)
if not db.get(constants.CONFIG_MOTION_SENSITIVITY):
    db.set(constants.CONFIG_MOTION_SENSITIVITY, 100)
if not db.get(constants.CONFIG_MOTION_DELAY_SEC):
    db.set(constants.CONFIG_MOTION_DELAY_SEC, 60)
if not db.get(constants.CONFIG_MOTION_THRESHOLD):
    db.set(constants.CONFIG_MOTION_THRESHOLD, 10)
if not db.get(constants.CONFIG_MOTION_CAPTURE_THRESHOLD):
    db.set(constants.CONFIG_MOTION_CAPTURE_THRESHOLD, 3)

#capture timer
if not db.get(constants.CONFIG_TIMER_INTERVAL_MIN):
    db.set(constants.CONFIG_TIMER_INTERVAL_MIN, 30)


def get(key = None):
    if key is None:
        with open('db/config.db', 'r') as configdb:
            configs = configdb.read()

        return json.loads(configs)
    else:
        value = db.get(key)
        if value == "true":
            return True
        elif value == "false":
            return False
        else:
            return db.get(key)

def update(configs):
    logger.info("Updating configs")

    if not configs or configs is None:
        logger.info("No configs to update")
        return

    for key, value in configs.iteritems():
        db.set(key, value)


