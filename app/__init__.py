import pickledb
from flask import Flask
from flask_restful import Api
from flask_jsglue import JSGlue

flask = Flask(__name__, static_folder='static', static_url_path='')
api = Api(flask)
jsglue = JSGlue(flask)

db = pickledb.load('yeti.db', True)

# set default configuration
if not db.get('UPLOAD_FOLDER'):
    db.set('UPLOAD_FOLDER', '/var/www/yeti-cam/uploads');

if not db.get('ALLOWED_EXTENSIONS'):
    db.set('ALLOWED_EXTENSIONS', ['jpg', 'jpeg'])

if not db.get('status'):
    db.dcreate('status')

from app import apis
from app import content

flask.config['UPLOAD_FOLDER'] = db.get('UPLOAD_FOLDER')
flask.config['ALLOWED_EXTENSIONS'] = db.get('ALLOWED_EXTENSIONS')

api.add_resource(apis.ImageApi, '/api/image')
api.add_resource(apis.ConfigApi, '/api/config')
api.add_resource(apis.StatusApi, '/api/status')


