__author__ = 'chris'
import pickledb
from datetime import datetime, timedelta
import yeti
from yeti.common import constants

import logging
logger = logging.getLogger(__name__)

class MotionLog:
    def __init__(self):
        logger.info("Initializing MotionLog")
        self.db = pickledb.load(yeti.getcamdir('db') + '/motion.db', True)

        if not self.db.get(constants.MOTION_LOG):
            self.db.lcreate(constants.MOTION_LOG)
    
    def add_motion_event(self, event_time):
        self.db.ladd(constants.MOTION_LOG, event_time)

    def get_motion_events_from(self, hours):
        total = 0
        for idx, event in enumerate(self.db.lgetall(constants.MOTION_LOG)):
            event_date = datetime.strptime(event, "%Y-%m-%dT%H:%M:%S.%f")
            delta_date = datetime.now() - timedelta(hours=hours)
            if event_date >= delta_date:
                total += 1
            else:
                self.db.lpop(constants.MOTION_LOG, idx)

        return total

    def get_all_motion_events(self):
        return self.db.lgetall(constants.MOTION_LOG)