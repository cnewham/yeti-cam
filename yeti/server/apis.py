import os
import json
from flask_restful import Resource, abort, request, reqparse
from flask import url_for, jsonify
from yeti.server import flask
from yeti.server import db
from yeti.common import constants, config

class ImageApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(constants.STATUS_CAM, type=str, required=False)

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
            upload = request.files['images']
            if upload and self.allowed_file(upload.filename):
                filename = upload.filename
                upload.save(os.path.join(flask.config['UPLOAD_FOLDER'], filename))
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
    def put(self):
        try:
            config.update(request.json)
            return 201
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)

    def get(self):
        try:
            return jsonify(config.get())
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)

class StatusApi(Resource):
    def post(self):
        try:
            status = request.json
            print json.dumps(status)
            return 201
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)

    def get(self):
        try:
            return jsonify(db.dgetall(constants.STATUS))
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)