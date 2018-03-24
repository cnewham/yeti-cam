import pickledb, datetime, os, errno
from flask import Flask
import yeti
from yeti.common import constants
import logging
logger = logging.getLogger(__name__)

logger.info("Starting yeti-cam-server...")

app = Flask(__name__, static_folder='www/static', template_folder='www/templates')


def initialize(name=None):
    logger.info("Running first time server initialization for cam: %s" % name)

    if name is None:
        db = pickledb.load(yeti.get_resource(path="server.db"), True)
    else:
        db = pickledb.load(yeti.get_cam_resource(name, path="db/server.db"), True)
        if not db.get('UPLOAD_FOLDER'):
            db.set('UPLOAD_FOLDER', yeti.get_cam_resource(name, path="uploads", dir_only=True))

        if not db.get('CAM_LOG_FOLDER'):
            db.set('CAM_LOG_FOLDER', yeti.get_cam_resource(name, path="logs", dir_only=True))

    if not db.get('SERVER_NAME'):
        db.set('SERVER_NAME', 'localhost')

    if not db.get('SOCKET_PORT'):
        db.set('SOCKET_PORT', 5001)

    if not db.get(constants.GDRIVE_FOLDER):
        db.set(constants.GDRIVE_FOLDER, '')

    if not db.get(constants.ENABLE_GDRIVE):
        db.set(constants.ENABLE_GDRIVE, False)

    if not db.get(constants.STATUS):
        db.dcreate(constants.STATUS)

    if not db.get(constants.LAST_CAM_UPDATE):
        db.set(constants.LAST_CAM_UPDATE, datetime.datetime.now().isoformat())

    return db


# Initial server init
db = initialize()

app.config['UPLOAD_FOLDER'] = db.get('UPLOAD_FOLDER')
app.config['CAM_LOG_FOLDER'] = db.get('CAM_LOG_FOLDER')
app.config['ALLOWED_EXTENSIONS'] = ['jpg', 'jpeg', 'txt', 'h264']
app.config['SOCKET_PORT'] = db.get('SOCKET_PORT')
app.config['SECRET_KEY'] = 'secret!'

