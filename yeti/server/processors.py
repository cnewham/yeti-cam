__author__ = 'chris'
import os
import shutil
import logging
import yeti
import pickledb
import datetime
from yeti.common import constants
from yeti.server import drive, motion

logger = logging.getLogger(__name__)

motion_log = motion.MotionLog()


class UploadProcessor:
    def __init__(self):
        logger.info("Initializing UploadProcessor")

    def process_image(self, event, upload, name=None):
        filename = None

        try:
            uploaddir = '%s/uploads' % yeti.getcamdir(name)
            db = pickledb.load('%s/db/server.db' % yeti.getcamdir(name), True)

            filename = "%s-%s" % (event,  os.path.basename(upload.filename))
            logger.info("Processing %s event for image %s" % (event, filename))
            capture = os.path.join(uploaddir, filename)
            upload.save(capture)
            shutil.copy(capture, os.path.join(uploaddir, "current.jpg"))

            if db.get(constants.ENABLE_GDRIVE):
                drive.upload(capture, event, db.get(constants.GDRIVE_FOLDER))
                os.remove(capture)
        except:
            logger.exception("An exception occurred during processing image upload for %s" % filename)

        if event == constants.EVENT_MOTION:
            motion_log.add_motion_event(datetime.datetime.now().isoformat())

        return filename

    def process_video(self, event, upload, name=None):
        filename = None

        try:
            uploaddir = '%s/uploads' % yeti.getcamdir(name)
            db = pickledb.load('%s/db/server.db' % yeti.getcamdir(name), True)

            filename = "%s-%s" % (event, os.path.basename(upload.filename))
            logger.info("Processing %s event for video %s" % (event, filename))
            recording = os.path.join(uploaddir, filename)
            upload.save(recording)

            if db.get(constants.ENABLE_GDRIVE):
                drive.upload(recording, event, db.get(constants.GDRIVE_FOLDER))
                os.remove(recording)

        except:
            logger.exception("An exception occurred during processing video upload for %s" % filename)

        if event == constants.EVENT_MOTION:
            motion_log.add_motion_event(datetime.datetime.now().isoformat())

        return filename


class StatusProcessor:
    def __init__(self):
        logger.info("Initializing StatusProcessor")

    def process(self, status, name=None):
        logger.info("Processing status %s" % status)

        db = pickledb.load('%s/db/server.db' % yeti.getcamdir(name), True)

        db.drem(constants.STATUS)
        db.dcreate(constants.STATUS)

        db.dadd(constants.STATUS, ("Motion Events (24hr)", motion_log.get_motion_events_from(24)))

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
