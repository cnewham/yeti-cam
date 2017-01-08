import os
from datetime import datetime, timedelta
import pickledb
from flask_restful import Resource, abort, request, reqparse
from flask import url_for, jsonify
from werkzeug import exceptions
import yeti
from yeti.server import weather, uploads, statuses, rabbitmq, app
from yeti.common import constants, config

import logging
logger = logging.getLogger(__name__)

class CaptureApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("event", type=str, required=True, location="form")

    def get(self, name=None):
        try:
            if name and not yeti.camdirexists(name):
                return {'error': '\"%s\" cam does not exist' % name}, 404

            response = []
            if not name:
                for cam in yeti.getnames():
                    response.append({"name": cam, "url": url_for("upload_folder", name=cam, filename="current.jpg")})
            else:
                response.append({"name": name, "url": url_for("upload_folder", name=name, filename="current.jpg")})

            return response
        except Exception as ex:
            logger.exception("An error occurred while attempting to send image")
            abort(400)

    def post(self, name=yeti.options.name):
        try:
            logger.debug("Name: " + name)

            args = self.parser.parse_args(request)
            uploaded = request.files['uploads']

            if uploaded and self.allowed_file(uploaded.filename):
                if uploaded.content_type in ("image/jpg","image/jpeg"):
                    filename = uploads.process_image(args["event"], uploaded, name)
                elif uploaded.content_type == "video/h264":
                    filename = uploads.process_video(args["event"], uploaded, name)
                else:
                    return {'error':'Unsupported capture type: %s' % uploaded.content_type}, 400

                with rabbitmq.EventHandler() as queue:
                    queue.send("camera_capture", {"event": args["event"], "name": name})

                return {'filename' : filename}, 201
            else:
                abort(400)
        except exceptions.HTTPException:
            raise
        except Exception as ex:
            logger.exception("An error occurred while attempting to receive uploaded image")
            abort(500)

    def allowed_file(self,filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


class ConfigApi(Resource):
    def get(self, name=None):
        try:

            if name and not yeti.camdirexists(name):
                return {'error': '\"%s\" cam does not exist' % name}, 404

            response = []
            if not name:
                for cam in yeti.getnames():
                    response.append({"name": cam, "url": url_for("configapi.v2", name=cam)})
            else:
                response = jsonify(config.get(name=name))

            return response

        except exceptions.HTTPException:
            raise
        except Exception as ex:
            logger.exception("An error occurred while attempting to send configs")
            abort(500)

    def put(self, name=yeti.options.name):
        try:
            logger.debug("Name: " + name)

            result = config.update(request.json, name)
            config.set_status(constants.CONFIG_STATUS_MODIFIED, name)
            if result:
                return {'error': result}, 409
            else:
                return 204
        except exceptions.HTTPException:
            raise
        except ValueError as ex:
            logger.exception("Invalid configuration object")
            abort(400)
        except Exception as ex:
            logger.exception("An error occurred while attempting to update config")
            abort(500)

    def patch(self, name=yeti.options.name):
        try:
            logger.debug("Name: " + name)

            if not request.json["status"]:
                abort(400)

            result = config.set_status(request.json["status"], name)
            if result:
                return {'error': result}, 409
            else:
                return {'status': config.get_status(name)}, 204
        except exceptions.HTTPException:
            raise
        except ValueError as ex:
            logger.exception("Invalid configuration object")
            abort(400)
        except Exception as ex:
            logger.exception("An error occurred while attempting to update config")
            abort(500)


class StatusApi(Resource):
    def get(self, name=None):
        try:

            if name and not yeti.camdirexists(name):
                return {'error': '\"%s\" cam does not exist' % name}, 404

            response = []
            if not name:
                for cam in yeti.getnames():
                    response.append({"name": cam, "url": url_for("statusapi.v2", name=cam)})
            else:
                db = pickledb.load('%s/db/server.db' % yeti.getcamdir(name), True)
                response = db.dgetall(constants.STATUS)

            return response
        except exceptions.HTTPException:
            raise
        except Exception as ex:
            logger.exception("An error occurred while attempting to send status")
            abort(500)

    def post(self, name=yeti.options.name):
        try:
            logger.debug("Name: " + name)

            status = request.json
            statuses.process(status, name)

            with rabbitmq.EventHandler() as queue:
                queue.send("status_update", {"name": name, "status": status})

            return 201
        except exceptions.HTTPException:
            raise
        except ValueError as ex:
            logger.exception("Could not parse status request from cam client")
            abort(400)
        except Exception as ex:
            logger.exception("An error occurred while attempting to update status from cam client")
            abort(500)


class WeatherApi(Resource):
    def get(self):
        try:
            return weather.get()
        except exceptions.HTTPException:
            raise
        except Exception as ex:
            logger.exception("An error occurred while attempting to retrieve weather updates")
            abort(500)

