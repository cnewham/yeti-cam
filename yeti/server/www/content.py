import os
import yeti
from yeti.server import drive
from yeti.server import app, db
from flask import render_template, send_from_directory, url_for, request, redirect

import logging
logger = logging.getLogger(__name__)


@app.route('/')
def index():
    try:
        return render_template('viewer.html')
    except Exception as ex:
            print type(ex)
            print ex
            return 500


@app.route('/configure')
def configure():
    try:
        return render_template('configure.html')
    except Exception as ex:
            print type(ex)
            print ex
            return 500


@app.route('/drive/auth')
def google_drive_auth():
    auth = drive.Authorize(url_for('google_drive_auth', _external=True))
    code = request.args.get('code')
    error = request.args.get('error')
    
    try:
        if error:
            logger.error("An error occurred while attempting to authorize Google Drive: %s" % error)
            return error
        elif code:
            logger.info("Updating credentials with code %s" % code)
            auth.complete(code)
            return redirect(url_for('index'))
    except Exception as ex:
        return ex.message, 401

    return redirect(auth.start())


@app.route('/uploads/<path:name>/<path:filename>')
def upload_folder(name, filename):
    try:
        directory = yeti.getcamdir(name) + "/uploads"
        return send_from_directory(directory, filename)
    except Exception as ex:
        print type(ex)
        print ex
        return 404
