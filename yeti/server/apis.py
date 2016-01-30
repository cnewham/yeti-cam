import os
from flask_restful import Resource, abort, request, reqparse
from flask import url_for
from yeti.server import flask
from yeti.server import db
from yeti.common import constants, config

class ImageApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(constants.STATUS_CAM, type=str, required=False)
        self.parser.add_argument(constants.STATUS_EVENT, type=str, location='form', required=False)
        self.parser.add_argument(constants.STATUS_BATTERY, type=str, location='form', required=False)
        self.parser.add_argument(constants.STATUS_TIME, type=str, location='form', required=False)

    def get(self):
        try:
            args = self.parser.parse_args()
            if args and args[constants.STATUS_CAM]:
                current = args.get(constants.STATUS_CAM) + "-current.jpg"
            else:
                current = "current.jpg"
            return url_for("upload_folder", filename=current)
        except Exception as ex:
            print type(ex)
            print ex
            abort(400)

    def post(self):
        try:
            upload = request.files['userfile']
            args = self.parser.parse_args()
            if upload and self.allowed_file(upload.filename):
                filename = upload.filename
                upload.save(os.path.join(flask.config['UPLOAD_FOLDER'], filename))
                db.dadd(constants.STATUS, ('Last Updated', args.get(constants.STATUS_TIME)))
                db.dadd(constants.STATUS, ('Battery', args.get(constants.STATUS_BATTERY)))
                db.dadd(constants.STATUS, ('Event', args.get(constants.STATUS_EVENT)))
                return 201
            else:
                abort(400)
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)

    def allowed_file(self,filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in flask.config['ALLOWED_EXTENSIONS']


class ConfigApi(Resource):
    def post(self):
        try:
            config.update(request.data)
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)
    def get(self):
        try:
            return config.get()
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)

class StatusApi(Resource):
    def get(self):
        try:
            return db.dgetall(constants.STATUS)
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)