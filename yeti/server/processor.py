__author__ = 'chris'
import os, shutil
from yeti.server import db

import logging
logger = logging.getLogger(__name__)

class UploadProcessor:
    def __init__(self):
        logger.info("Initializing UploadProcessor")

    def process(self, event, filename):
        logger.info("Processing %s event for image %s" % (event, filename))
        shutil.copy(os.path.join(db.get('UPLOAD_FOLDER'), "current.jpg"), os.path.join(db.get('UPLOAD_FOLDER'), "%s-%s" % (event, filename)))
