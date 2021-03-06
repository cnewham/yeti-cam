﻿import os
from datetime import datetime, timedelta
from flask_restful import Resource, abort, request, reqparse
from flask import url_for, jsonify
from werkzeug import exceptions
import yeti
from yeti.server import uploads, statuses, rabbitmq, app
from yeti.common import constants, config

import logging
logger = logging.getLogger(__name__)

class CaptureApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(constants.STATUS_CAM, type=str, required=False)
        self.parser.add_argument("event", type=str, required=True, location="form")

    def get(self):
        try:
            args = self.parser.parse_args()
            if args and args[constants.STATUS_CAM]:
                current = args.get(constants.STATUS_CAM) + "-current.jpg"
            else:
                current = "current.jpg"
            return url_for("upload_folder", filename=current)
        except Exception as ex:
            logger.exception("An error occurred while attempting to send image")
            abort(400)

    def post(self):
        try:
            args = self.parser.parse_args(request)
            uploaded = request.files['uploads']

            if uploaded and self.allowed_file(uploaded.filename):
                if uploaded.content_type in ("image/jpg","image/jpeg"):
                    filename = uploads.process_image(args["event"], uploaded)
                elif uploaded.content_type == "video/h264":
                    filename = uploads.process_video(args["event"], uploaded)
                else:
                    return {'error':'Unsupported capture type: %s' % uploaded.content_type}, 400

                with rabbitmq.EventHandler() as queue:
                    queue.send("camera_capture", {"event": args["event"], "name": yeti.options.name})

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

#Depreciated
class ImageApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument(constants.STATUS_CAM, type=str, required=False)
        self.parser.add_argument("event", type=str, required=True, location="form")

    def get(self):
        try:
            args = self.parser.parse_args()
            if args and args[constants.STATUS_CAM]:
                current = args.get(constants.STATUS_CAM) + "-current.jpg"
            else:
                current = "current.jpg"
            return url_for("upload_folder", filename=current)
        except Exception as ex:
            logger.exception("An error occurred while attempting to send image")
            abort(400)

    def post(self):
        try:
            args = self.parser.parse_args(request)
            upload = request.files['images']
            if upload and self.allowed_file(upload.filename):
                filename = uploads.process_image(args["event"], upload)
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
    def put(self):
        try:
            result = config.update(request.json)
            config.set_status(constants.CONFIG_STATUS_MODIFIED)
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

    def patch(self):
        try:
            if not request.json["status"]:
                abort(400)

            result = config.set_status(request.json["status"])
            if result:
                return {'error': result}, 409
            else:
                return {'status':config.get_status()}, 204
        except exceptions.HTTPException:
            raise
        except ValueError as ex:
            logger.exception("Invalid configuration object")
            abort(400)
        except Exception as ex:
            logger.exception("An error occurred while attempting to update config")
            abort(500)

    def get(self):
        try:
            return jsonify(config.get())
        except exceptions.HTTPException:
            raise
        except Exception as ex:
            logger.exception("An error occurred while attempting to send configs")
            abort(500)

class StatusApi(Resource):
    def post(self):
        try:
            status = request.json
            statuses.process(status)

            with rabbitmq.EventHandler() as queue:
                queue.send("status_update",{"name": yeti.options.name, "status": status})

            return 201
        except exceptions.HTTPException:
            raise
        except ValueError as ex:
            logger.exception("Could not parse status request from cam client")
            abort(400)
        except Exception as ex:
            logger.exception("An error occurred while attempting to update status from cam client")
            abort(500)

    def get(self):
        try:
            return jsonify(db.dgetall(constants.STATUS))
        except exceptions.HTTPException:
            raise
        except Exception as ex:
            logger.exception("An error occurred while attempting to send status")
            abort(500)
