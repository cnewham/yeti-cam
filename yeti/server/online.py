import yeti
from yeti import common

import logging
logger = logging.getLogger(__name__)

online = {}


def add(sid, name):
    logger.info("Camera (%s) - %s - added" % (name, sid))
    global online

    online[sid] = {"name": name, "connected": True}


def update(sid, connected):
    logger.info("Updating camera status (%s) - connected: %s" % (sid, connected))

    if sid in online:
        online[sid]["connected"] = connected


def remove(sid):
    logger.info("Removing camera (%s)" % sid)
    global online

    if sid in online:
        del online[sid]


def get():
    return online.values()
