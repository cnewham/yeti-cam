__author__ = 'chris'
import pickledb
import json
from yeti.common import constants, log

db = pickledb.load('db/config.db', True)

if not db.get(constants.CONFIG_VERSION):
    db.set(constants.CONFIG_VERSION, 1)
if not db.get(constants.CONFIG_SERVER):
    db.set(constants.CONFIG_SERVER, "http://localhost:5000/api/")
if not db.get(constants.CONFIG_IMAGE_DIR):
    db.set(constants.CONFIG_IMAGE_DIR, "/home/pi/yeti/images")
if not db.get(constants.CONFIG_CAPTURE_INTERVAL_MIN):
    db.set(constants.CONFIG_CAPTURE_INTERVAL_MIN, 30)

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


