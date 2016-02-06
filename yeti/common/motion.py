__author__ = 'chris'
import pickledb
from datetime import datetime, timedelta
from yeti.common import config, constants


import logging
logger = logging.getLogger(__name__)

class MotionLog:
    def __init__(self):
        logger.info("Initializing MotionLog")
        self.db = pickledb.load('db/motion.db', True)

        if not self.db.get(constants.MOTION_LOG):
            self.db.lcreate(constants.MOTION_LOG)
    
    def add_motion_event(self, event_time):
        self.db.ladd(constants.MOTION_LOG, event_time);

    def get_motion_events_from(self, hours):
        total = 0
        for event in self.db.lgetall(constants.MOTION_LOG):
            event_date = datetime.strptime(event, "%Y-%m-%dT%H:%M:%S.%f")
            delta_date = datetime.now() - timedelta(hours=hours)
            if event_date >= delta_date:
                total += 1
            else:
                self.db.lpop(constants.MOTION_LOG, event)

        return total

class MotionEvents:
    def __init__(self):
        self.motion_events = 0
        self.last_motion_event = None

    def enabled(self):
        #logger.debug("MotionEvents: last_motion_event: %s, motion_events: %s" % (self.last_motion_event, self.motion_events))

        if self.last_motion_event is None or self.exceeds_motion_capture_delay():
            self.motion_events = 1
            self.last_motion_event = datetime.now()
            #logger.debug("MotionsEvents: enabled - doesn't exceed motion capture delay")
            return True
        elif self.motion_events + 1 <= config.get(constants.CONFIG_MOTION_CAPTURE_THRESHOLD):
            self.motion_events += 1
            self.last_motion_event = datetime.now()
            #logger.debug("MotionsEvents: enabled - still within motion capture threshold")
            return True
        else:
            #logger.debug("MotionsEvents: disabled")
            return False

    def exceeds_motion_capture_delay(self):
        if self.last_motion_event is not None:
            delta_date = datetime.now() - timedelta(seconds=config.get(constants.CONFIG_MOTION_DELAY_SEC))
            #logger.debug("MotionEvents: delta_date: %s" % delta_date)
            return delta_date > self.last_motion_event
        else:
            return True