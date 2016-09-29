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
if not db.get(constants.CONFIG_STATUS):
    db.set(constants.CONFIG_STATUS, constants.CONFIG_STATUS_NEW)
if not db.get(constants.CONFIG_CHECK_INTERVAL_MIN):
    db.set(constants.CONFIG_CHECK_INTERVAL_MIN, 60)
if not db.get(constants.CONFIG_SERVER):
    db.set(constants.CONFIG_SERVER, "http://localhost:5000/api/")
if not db.get(constants.CONFIG_SOCKET_HOST):
    db.set(constants.CONFIG_SOCKET_HOST, "localhost")
if not db.get(constants.CONFIG_SOCKET_PORT):
    db.set(constants.CONFIG_SOCKET_PORT, 5001)

#image
if not db.get(constants.CONFIG_IMAGE_DIR):
    db.set(constants.CONFIG_IMAGE_DIR, "/home/yeti/cam/images")
if not db.get(constants.CONFIG_IMAGE_PREFIX):
    db.set(constants.CONFIG_IMAGE_PREFIX, "capture-")
if not db.get(constants.CONFIG_IMAGE_WIDTH):
    db.set(constants.CONFIG_IMAGE_WIDTH, 1980)
if not db.get(constants.CONFIG_IMAGE_HEIGHT):
    db.set(constants.CONFIG_IMAGE_HEIGHT, 1080)
if not db.get(constants.CONFIG_IMAGE_VFLIP) is None:
    db.set(constants.CONFIG_IMAGE_VFLIP, False)
if not db.get(constants.CONFIG_IMAGE_HFLIP is None):
    db.set(constants.CONFIG_IMAGE_HFLIP, False)
if not db.get(constants.CONFIG_IMAGE_QUALITY):
    db.set(constants.CONFIG_IMAGE_QUALITY, 85)
if not db.get(constants.CONFIG_IMAGE_EXPOSURE_MODE):
    db.set(constants.CONFIG_IMAGE_EXPOSURE_MODE, "auto")
if not db.get(constants.CONFIG_IMAGE_AWB_MODE):
    db.set(constants.CONFIG_IMAGE_AWB_MODE, "auto")

#motion
if db.get(constants.CONFIG_MOTION_ENABLED) is None:
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
if not db.get(constants.CONFIG_MOTION_EVENT_CAPTURE_TYPE):
    db.set(constants.CONFIG_MOTION_EVENT_CAPTURE_TYPE, constants.EVENT_TYPE_IMAGE)
if not db.get(constants.CONFIG_MOTION_PERCENT_CHANGE_MAX):
    db.set(constants.CONFIG_MOTION_PERCENT_CHANGE_MAX, 40)

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

def version():
    return get(constants.CONFIG_VERSION)

def get_status():
    return get(constants.CONFIG_STATUS)

def set_status(status):
    db.set(constants.CONFIG_STATUS, status)
    db.dump()

def update(configs):
    logger.info("Updating configs")

    if not configs or configs is None:
        return "No config values have been supplied";

    if configs[constants.CONFIG_VERSION] <= version():
        return "config updated by another user. Please try again"

    for key, value in configs.iteritems():
        db.set(key, value)

    db.dump()


