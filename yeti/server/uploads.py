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

def process_image(event, upload, name=None):
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

def process_video(event, upload, name=None):
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
