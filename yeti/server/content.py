import os
from yeti.server import flask
from flask import render_template, send_from_directory

@flask.route('/')
def index():
    try:
        return render_template('viewer.html')
    except Exception as ex:
            print type(ex)
            print ex
            return 500

@flask.route('/uploads/<path:filename>')
def upload_folder(filename):
    try:
        return send_from_directory(os.path.join(os.path.dirname(flask.root_path), flask.config["UPLOAD_FOLDER"]), filename)
    except Exception as ex:
        print type(ex)
        print ex
        return 404
