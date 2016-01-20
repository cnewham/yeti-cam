import os
import datetime
from flask_restful import Resource, abort, request, reqparse
from flask import url_for
from app import flask
from app import db

class ImageApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('cam', type=str, required=False)
        self.parser.add_argument('battery', type=str, location='form', required=False)
        self.parser.add_argument('event', type=str, location='form', required=False)
        self.parser.add_argument('time', type=str, location='form', required=False)

    def get(self):
        try:
            args = self.parser.parse_args()
            if args and args['cam']:
                current = args.get('cam') + "-current.jpg"
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
                db.dadd('status', ('Last Updated', args.get('time')))
                db.dadd('status', ('Battery', args.get('battery')))
                db.dadd('status', ('Event', args.get('event')))
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
    def get(self):
        try:
            return flask.send_static_file("config.txt")
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)

class StatusApi(Resource):
    def get(self):
        try:
            return db.dgetall('status')
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)

    def post(self):
        try:
            #TODO: implement post request
            db.dadd('status', ('temp',20))
            db.dadd('status', ('temp',21))
            db.dadd('status', ('humidity',30))
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)
