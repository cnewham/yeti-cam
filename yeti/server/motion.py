__author__ = 'chris'
import pickledb
from datetime import datetime, timedelta
import yeti
from yeti.common import constants

import logging
logger = logging.getLogger(__name__)

db = pickledb.load(yeti.createcamdir('db') + '/motion.db', True)

if not db.get(constants.MOTION_LOG):
    db.lcreate(constants.MOTION_LOG)


def add_motion_event(event_time):
    db.ladd(constants.MOTION_LOG, event_time)


def get_motion_events_from(hours):
    total = 0
    for idx, event in enumerate(db.lgetall(constants.MOTION_LOG)):
        event_date = datetime.strptime(event, "%Y-%m-%dT%H:%M:%S.%f")
        delta_date = datetime.now() - timedelta(hours=hours)
        if event_date >= delta_date:
            total += 1
        else:
            db.lpop(constants.MOTION_LOG, idx)

    return total


def get_all_motion_events():
    return db.lgetall(constants.MOTION_LOG)