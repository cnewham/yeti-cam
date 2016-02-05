__author__ = 'chris'
import os, shutil, datetime
from yeti.common import constants, motion
from yeti.server import db

import logging
logger = logging.getLogger(__name__)

motion_log = motion.MotionLog()

class UploadProcessor:
    def __init__(self):
        logger.info("Initializing UploadProcessor")

    def process(self, event, filename):
        logger.info("Processing %s event for image %s" % (event, filename))
        shutil.copy(os.path.join(db.get('UPLOAD_FOLDER'), "current.jpg"), os.path.join(db.get('UPLOAD_FOLDER'), "%s-%s" % (event, filename)))

        if event == constants.EVENT_MOTION:
            motion_log.add_motion_event(datetime.datetime.now())


class StatusProcessor:
    def __init__(self):
        logger.info("Initializing StatusProcessor")

    def process(self, status):
        logger.info("Processing status %s" % status)
        db.drem(constants.STATUS)
        db.dcreate(constants.STATUS)

        for key, value in status.iteritems():
            if key == constants.STATUS_EVENT:
                db.dadd(constants.STATUS, ("Event", value))
            elif key == constants.STATUS_TIME:
                date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                db.dadd(constants.STATUS, ("Time", date.strftime('%m-%d-%Y %I:%M %p')))
            elif key == constants.STATUS_INDOOR_TEMP:
                db.dadd(constants.STATUS, ("Indoor Temp", "%.2f%sF, %.2f%%" % (value[constants.STATUS_TEMP], unichr(176), value[constants.STATUS_HUMIDITY])))
            elif key == constants.STATUS_OUTDOOR_TEMP:
                db.dadd(constants.STATUS, ("Outdoor Temp", "%.2f%sF, %.2f%%" % (value[constants.STATUS_TEMP], unichr(176), value[constants.STATUS_HUMIDITY])))
            elif key == constants.STATUS_MOTION_EVENTS_24H:
                db.dadd(constants.STATUS, ("Motion Events", motion_log.get_motion_events_from(24)))
            else:
                db.dadd(constants.STATUS, (key, value))

class LogProcessor:
    def __init__(self):
        logger.info("Initializing LogProcessor")

    def process(self, logfile):
        logger.info("Processing logfile %s" % logfile)
        #TODO: implement log file processor
