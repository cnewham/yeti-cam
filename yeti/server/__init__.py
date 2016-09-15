import pickledb, datetime, os
from flask import Flask
from yeti.common import constants
import logging
logger = logging.getLogger(__name__)

logger.info("Starting yeti-cam-server...")

app = Flask(__name__, static_folder='www/static', template_folder='www/templates')

# initialize default directories
if not os.path.exists("db"):
    os.makedirs("db")

if not os.path.exists("uploads"):
    os.makedirs("uploads")

# initialize configuration
db = pickledb.load('db/server.db', True)

if not db.get('SERVER_NAME'):
    db.set('SERVER_NAME', 'localhost:5000');

if not db.get('UPLOAD_FOLDER'):
    db.set('UPLOAD_FOLDER', '/var/www/yeti-cam/uploads');

if not db.get('CAM_LOG_FOLDER'):
    db.set('CAM_LOG_FOLDER', '/var/www/yeti-cam/logs');

if not db.get('ALLOWED_EXTENSIONS'):
    db.set('ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'txt', 'h264'])

if not db.get(constants.GDRIVE_FOLDER):
    db.set(constants.GDRIVE_FOLDER, '')

if not db.get(constants.ENABLE_GDRIVE):
    db.set(constants.ENABLE_GDRIVE, False)

if not db.get(constants.STATUS):
    db.dcreate(constants.STATUS)

if not db.get(constants.LAST_CAM_UPDATE):
    db.set(constants.LAST_CAM_UPDATE, datetime.datetime.now().isoformat())

app.config['UPLOAD_FOLDER'] = db.get('UPLOAD_FOLDER')
app.config['CAM_LOG_FOLDER'] = db.get('CAM_LOG_FOLDER')
app.config['ALLOWED_EXTENSIONS'] = db.get('ALLOWED_EXTENSIONS')
app.config['SECRET_KEY'] = 'secret!'