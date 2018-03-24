__author__ = 'chris'
import os
import yeti
import logging
import logging.handlers

LOG_DIR = yeti.get_cam_resource(path='logs', dir_only=True)
LOG_LEVEL = logging.INFO
LOG_FILENAME = "%s/yeticam.log" % LOG_DIR

#configure logging
logging.basicConfig(level=LOG_LEVEL,
                    format="%(name)-12s: %(levelname)-8s %(message)s")

handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=500000, backupCount=5)

formatter = logging.Formatter("%(asctime)-15s %(levelname)-8s %(name)-20s %(message)s")
handler.setFormatter(formatter)

logging.getLogger('').addHandler(handler)


