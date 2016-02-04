import pickledb
from flask import Flask
from flask_restful import Api
from flask_jsglue import JSGlue
from yeti.common import constants
import logging
logger = logging.getLogger(__name__)

flask = Flask(__name__, static_folder='static', static_url_path='')
api = Api(flask)
jsglue = JSGlue(flask)

db = pickledb.load('db/server.db', True)

# set default configuration
if not db.get('UPLOAD_FOLDER'):
    db.set('UPLOAD_FOLDER', '/var/www/yeti-cam/uploads');

if not db.get('CAM_LOG_FOLDER'):
    db.set('CAM_LOG_FOLDER', '/var/www/yeti-cam/logs');

if not db.get('ALLOWED_EXTENSIONS'):
    db.set('ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'txt'])

if not db.get(constants.STATUS):
    db.dcreate(constants.STATUS)

from yeti.server import apis
from yeti.server import content

flask.config['UPLOAD_FOLDER'] = db.get('UPLOAD_FOLDER')
flask.config['CAM_LOG_FOLDER'] = db.get('CAM_LOG_FOLDER')
flask.config['ALLOWED_EXTENSIONS'] = db.get('ALLOWED_EXTENSIONS')

api.add_resource(apis.ImageApi, '/api/image')
api.add_resource(apis.ConfigApi, '/api/config')
api.add_resource(apis.StatusApi, '/api/status')
api.add_resource(apis.LogApi, '/api/log')


