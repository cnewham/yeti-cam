﻿import pickledb
from flask import Flask, redirect
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

if not db.get(constants.GDRIVE_FOLDER):
    db.set(constants.GDRIVE_FOLDER, '')

if not db.get(constants.STATUS):
    db.dcreate(constants.STATUS)

#Load content
from yeti.server import apis, content
from yeti.server import drive

flask.config['UPLOAD_FOLDER'] = db.get('UPLOAD_FOLDER')
flask.config['CAM_LOG_FOLDER'] = db.get('CAM_LOG_FOLDER')
flask.config['ALLOWED_EXTENSIONS'] = db.get('ALLOWED_EXTENSIONS')

api.add_resource(apis.ImageApi, '/api/image')
api.add_resource(apis.ConfigApi, '/api/config')
api.add_resource(apis.StatusApi, '/api/status')
api.add_resource(apis.LogApi, '/api/log')

@flask.route('/drive/auth')
def google_drive_auth():
    auth = drive.Authorize(flask.url_for('drive/auth', _external=True))
    code = flask.request.args.get('code')
    error = flask.request.args.get('error')
    
    if error:
        logger.error("An error occurred while attempting to authorize Google Drive: %s" % error)
        return
    elif code:
        logger.info("Updating credentials with code %s" % code)
        auth.complete(code)
        return

    return redirect(auth.start())

