import logging
import yeti
import pickledb
import datetime
from yeti.common import constants
from yeti.server import motion

logger = logging.getLogger(__name__)


def process(status, name=None):
    logger.info("Processing status %s" % status)

    db = pickledb.load('%s/db/server.db' % yeti.getcamdir(name), True)

    db.drem(constants.STATUS)
    db.dcreate(constants.STATUS)

    db.dadd(constants.STATUS, ("Motion Events (24hr)", motion.get_motion_events_from(24)))

    for key, value in status.iteritems():
        if key == constants.STATUS_EVENT:
            db.dadd(constants.STATUS, ("Event", value))
        elif key == constants.STATUS_TIME:
            date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
            db.set(constants.LAST_CAM_UPDATE, date.isoformat())
            db.dadd(constants.STATUS, ("Last Update", date.strftime('%m-%d-%Y %I:%M %p')))
        elif key == constants.STATUS_INDOOR_TEMP:
            db.dadd(constants.STATUS, ("Indoor Temp", "%.2f%sF, %.2f%%" % (value[constants.STATUS_TEMP], unichr(176), value[constants.STATUS_HUMIDITY])))
        elif key == constants.STATUS_OUTDOOR_TEMP:
            db.dadd(constants.STATUS, ("Outdoor Temp", "%.2f%sF, %.2f%%" % (value[constants.STATUS_TEMP], unichr(176), value[constants.STATUS_HUMIDITY])))
        else:
            db.dadd(constants.STATUS, (key, value))

    db.dump() #persist
