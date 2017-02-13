__author__ = 'chris'
import pickledb
from datetime import datetime, timedelta
import yeti
from yeti.common import constants

import logging
logger = logging.getLogger(__name__)

db = pickledb.load(yeti.createcamdir('db') + '/motion.db', True)


def add_motion_event(event_time, name=yeti.options.name):
    if not db.get(name):
        db.lcreate(name)

    db.ladd(name, event_time)


def get_motion_events_from(hours, name=yeti.options.name):
    if not db.get(name):
        db.lcreate(name)

    total = 0
    for idx, event in enumerate(db.lgetall(name)):
        event_date = datetime.strptime(event, "%Y-%m-%dT%H:%M:%S.%f")
        delta_date = datetime.now() - timedelta(hours=hours)
        if event_date >= delta_date:
            total += 1
        else:
            db.lpop(name, idx)

    return total


def get_all_motion_events(name=yeti.options.name):
    if not db.get(name):
        db.lcreate(name)

    return db.lgetall(name)