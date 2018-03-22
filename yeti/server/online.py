import yeti
from yeti import common

import logging
logger = logging.getLogger(__name__)

online = {}


def add(sid, name):
    logger.info("Camera (%s) connected: %s" % (name, sid))
    global online
    online[sid] = name


def remove(sid):
    logger.info("Camera disconnected: (%s)" % sid)
    global online

    if sid in online:
        del online[sid]


def get():
    return online.values()
