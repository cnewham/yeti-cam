__author__ = 'chris'
import pickledb
import json
import yeti
from yeti.common import constants
import logging
logger = logging.getLogger(__name__)

default = pickledb.load(yeti.get_cam_resource(path="db/config.db"), True)

# server/config

if not default.get(constants.CONFIG_SERVER):
    if yeti.options.server is not None:
        default.set(constants.CONFIG_SERVER, yeti.options.server)
    else:
        default.set(constants.CONFIG_SERVER, "http://localhost:5000/api/v2/")

if not default.get(constants.CONFIG_VERSION):
    default.set(constants.CONFIG_VERSION, 0)
if not default.get(constants.CONFIG_STATUS):
    default.set(constants.CONFIG_STATUS, constants.CONFIG_STATUS_NEW)
if not default.get(constants.CONFIG_CHECK_INTERVAL_MIN):
    default.set(constants.CONFIG_CHECK_INTERVAL_MIN, 60)
if not default.get(constants.CONFIG_SOCKET_HOST):
    default.set(constants.CONFIG_SOCKET_HOST, "localhost")
if not default.get(constants.CONFIG_SOCKET_PORT):
    default.set(constants.CONFIG_SOCKET_PORT, 5001)

# image
if not default.get(constants.CONFIG_IMAGE_DIR):
    default.set(constants.CONFIG_IMAGE_DIR, "/home/yeti/cam/images")
if not default.get(constants.CONFIG_IMAGE_PREFIX):
    default.set(constants.CONFIG_IMAGE_PREFIX, "capture-")
if not default.get(constants.CONFIG_IMAGE_WIDTH):
    default.set(constants.CONFIG_IMAGE_WIDTH, 1980)
if not default.get(constants.CONFIG_IMAGE_HEIGHT):
    default.set(constants.CONFIG_IMAGE_HEIGHT, 1080)
if default.get(constants.CONFIG_IMAGE_VFLIP) is None:
    default.set(constants.CONFIG_IMAGE_VFLIP, False)
if default.get(constants.CONFIG_IMAGE_HFLIP is None):
    default.set(constants.CONFIG_IMAGE_HFLIP, False)
if not default.get(constants.CONFIG_IMAGE_QUALITY):
    default.set(constants.CONFIG_IMAGE_QUALITY, 85)
if not default.get(constants.CONFIG_IMAGE_EXPOSURE_MODE):
    default.set(constants.CONFIG_IMAGE_EXPOSURE_MODE, "auto")
if not default.get(constants.CONFIG_IMAGE_AWB_MODE):
    default.set(constants.CONFIG_IMAGE_AWB_MODE, "auto")

# motion
if default.get(constants.CONFIG_MOTION_ENABLED) is None:
    default.set(constants.CONFIG_MOTION_ENABLED, True)
if not default.get(constants.CONFIG_MOTION_THRESHOLD):
    default.set(constants.CONFIG_MOTION_THRESHOLD, 10)
if not default.get(constants.CONFIG_MOTION_SENSITIVITY):
    default.set(constants.CONFIG_MOTION_SENSITIVITY, 100)
if not default.get(constants.CONFIG_MOTION_DELAY_SEC):
    default.set(constants.CONFIG_MOTION_DELAY_SEC, 60)
if not default.get(constants.CONFIG_MOTION_THRESHOLD):
    default.set(constants.CONFIG_MOTION_THRESHOLD, 10)
if not default.get(constants.CONFIG_MOTION_CAPTURE_THRESHOLD):
    default.set(constants.CONFIG_MOTION_CAPTURE_THRESHOLD, 3)
if not default.get(constants.CONFIG_MOTION_EVENT_CAPTURE_TYPE):
    default.set(constants.CONFIG_MOTION_EVENT_CAPTURE_TYPE, constants.EVENT_TYPE_IMAGE)
if not default.get(constants.CONFIG_MOTION_PERCENT_CHANGE_MAX):
    default.set(constants.CONFIG_MOTION_PERCENT_CHANGE_MAX, 40)

# capture timer
if not default.get(constants.CONFIG_TIMER_INTERVAL_MIN):
    default.set(constants.CONFIG_TIMER_INTERVAL_MIN, 30)

db = {}
for cam in yeti.get_registered_cams():
    db[cam] = pickledb.load(yeti.get_cam_resource(cam, "db/config.db"), True)


def get(key=None, name=yeti.options.name):
    if key is None:
        with open(yeti.get_cam_resource(name, "db/config.db"), 'r+') as configdb:
            configs = configdb.read()

        return json.loads(configs)
    else:
        value = db[name].get(key)
        if value == "true":
            return True
        elif value == "false":
            return False
        else:
            return db[name].get(key)


def version(name=yeti.options.name):
    return get(constants.CONFIG_VERSION, name)


def get_status(name=yeti.options.name):
    return get(constants.CONFIG_STATUS, name)


def set_status(status, name=yeti.options.name):
    db[name].set(constants.CONFIG_STATUS, status)
    db[name].dump()


def update(configs, name=yeti.options.name):
    logger.info("Updating configs")

    if name not in db:
        db[name] = pickledb.load(yeti.get_cam_resource(name, "db/config.db"), True)

    if not configs or configs is None:
        raise ValueError("No config values have been supplied")

    for key, value in configs.iteritems():
        db[name].set(key, value)

    db[name].dump()


