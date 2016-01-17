import os
from flask_restful import Resource, abort, request
from flask import url_for, send_from_directory
from app import flask

class ImageApi(Resource):
    def get(self):
        try:
            return url_for("upload_folder", filename="current.jpg")
        except Exception as ex:
            print type(ex)
            print ex
            abort(500)

    def post(self):
        try:
            upload = request.files['userfile']
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


class ConfigAPi(Resource):
    def get(self):
        return {'hello': 'world'}