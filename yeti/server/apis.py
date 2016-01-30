import os
import datetime
from flask_restful import Resource, abort, request, reqparse
from flask import url_for, jsonify
from yeti.server import flask
from yeti.server import db
from yeti.common import constants, config, log

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
            log.LogError(__name__, "An error occurred while attempting to send image", ex)
            abort(400)

    def post(self):
        try:
            upload = request.files['images']
            if upload and self.allowed_file(upload.filename):
                filename = upload.filename
                upload.save(os.path.join(flask.config['UPLOAD_FOLDER'], filename))
                return {}, 201
            else:
                abort(400)
        except ValueError as ex:
            log.LogError(__name__, "Could not parse status request from cam client", ex)
            abort(400)
        except Exception as ex:
            log.LogError(__name__, "An error occurred while attempting to receive uploaded image", ex)
            abort(500)

    def allowed_file(self,filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in flask.config['ALLOWED_EXTENSIONS']


class ConfigApi(Resource):
    def put(self):
        try:
            config.update(request.json)
            return {}, 201
        except ValueError as ex:
            log.LogError(__name__, "Could not parse status request from cam client", ex)
            abort(400)
        except Exception as ex:
            log.LogError(__name__, "An error occurred while attempting to update config from cam client", ex)
            abort(500)

    def get(self):
        try:
            return jsonify(config.get())
        except Exception as ex:
            log.LogError(__name__, "An error occurred while attempting to send configs", ex)
            abort(500)

class StatusApi(Resource):
    def post(self):
        try:
            status = request.json

            log.LogInfo(__name__, "Updating status from cam client")
            db.drem(constants.STATUS)
            db.dcreate(constants.STATUS)

            for key, value in status.iteritems():
                if key == constants.STATUS_EVENT:
                    db.dadd(constants.STATUS, ("Event", value))
                elif key == constants.STATUS_TIME:
                    date = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                    db.dadd(constants.STATUS, ("Time", date.strftime('%x %X %p')))
                elif key == constants.STATUS_INDOOR_TEMP:
                    db.dadd(constants.STATUS, ("Indoor Temp", "%s%sF %s%%" % (value[constants.STATUS_TEMP], unichr(176), value[constants.STATUS_HUMIDITY])))
                elif key == constants.STATUS_OUTDOOR_TEMP:
                    db.dadd(constants.STATUS, ("Outdoor Temp", "%s%sF %s%%" % (value[constants.STATUS_TEMP], unichr(176), value[constants.STATUS_HUMIDITY])))
                elif key == constants.STATUS_MOTION_EVENTS_24H:
                    db.dadd(constants.STATUS, ("Motion Events", value))
                else:
                    db.dadd(constants.STATUS, (key, value))
            return {}, 201
        except ValueError as ex:
            log.LogError(__name__, "Could not parse status request from cam client", ex)
            abort(400)
        except Exception as ex:
            log.LogError(__name__, "An error occurred while attempting to update status from cam client", ex)
            abort(500)

    def get(self):
        try:
            return jsonify(db.dgetall(constants.STATUS))
        except Exception as ex:
            log.LogError(__name__, "An error occurred while attempting to send status", ex)
            abort(500)