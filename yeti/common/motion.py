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
    
    def add_motion_event(self, event_time, filename):
        self.db.ladd(constants.MOTION_LOG, {filename : event_time}) #TODO: check if a kvp can be added to a pickledb list

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

class MotionEvents:
    def __init__(self):
        self.motion_events = 0
        self.last_motion_event = None

    def enabled(self):
        if not config.get(constants.CONFIG_MOTION_ENABLED):
            return False #motion disabled in configuration

        if self.last_motion_event is None or self.exceeds_motion_capture_delay():
            self.motion_events = 1
            self.last_motion_event = datetime.now()
            return True #doesn't exceed motion capture delay
        elif self.motion_events + 1 <= config.get(constants.CONFIG_MOTION_CAPTURE_THRESHOLD):
            self.motion_events += 1
            self.last_motion_event = datetime.now()
            return True #still within motion capture threshold
        else:
            return False #exceeds motion capture threshold

    def exceeds_motion_capture_delay(self):
        if self.last_motion_event is not None:
            delta_date = datetime.now() - timedelta(seconds=config.get(constants.CONFIG_MOTION_DELAY_SEC))
            return delta_date > self.last_motion_event
        else:
            return True