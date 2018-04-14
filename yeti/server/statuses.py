import logging
import yeti
import pickledb
import datetime
from flask import url_for
from yeti.common import constants
import yeti.server
from yeti.server import motion

logger = logging.getLogger(__name__)


def process(status, name=yeti.options.name):
    logger.info("Processing status %s" % status)

    if not yeti.resource_exists(yeti.get_cam_resource(name, "db/server.db")):
        yeti.server.initialize(name)

    db = pickledb.load(yeti.get_cam_resource(name, "db/server.db"), True)

    db.drem(constants.STATUS)
    db.dcreate(constants.STATUS)

    events = motion.get_motion_events_from(24, name)
    if events > 0:
        db.dadd(constants.STATUS, ("Motion Events", events))

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
            db.dadd(constants.STATUS, ("Outdoor Temp", "<a href='%s'>%.2f%sF, %.2f%%</a>"
                                       % (url_for('weather'),
                                          value[constants.STATUS_TEMP],
                                          unichr(176),
                                          value[constants.STATUS_HUMIDITY])))
        else:
            db.dadd(constants.STATUS, (key, value))

    db.dump()  # persist
