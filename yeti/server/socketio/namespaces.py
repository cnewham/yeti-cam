from yeti.server import online as cams
from flask_socketio import Namespace, emit, send
from flask import request

import logging
logger = logging.getLogger(__name__)


class Cam(Namespace):
    def on_connect(self):
        logger.info("Camera (%s) client connected" % request.sid)

    def on_disconnect(self):
        cams.remove(request.sid)
        emit('camera_status', cams.get(), namespace='/web', broadcast=True)

    def on_hello(self, name):
        logger.info("Camera (%s) [%s] said hello" % (request.sid, name))
        cams.add(request.sid, name)
        emit('camera_status', cams.get(), namespace='/web', broadcast=True)

    def on_goodbye(self, name):
        logger.info("Camera (%s) [%s] said goodbye" % (request.sid, name))
        cams.remove(request.sid)
        emit('camera_status', cams.get(), namespace='/web', broadcast=True)

    def on_config_updated(self, data):
        emit('config_updated', data, namespace='/web', broadcast=True)

    def on_manual_capture_result(self, data):
        emit('manual_capture_result', data, namespace='/web', broadcast=True)


class Web(Namespace):
    def on_connect(self):
        logger.info("Web client connected")
        emit('camera_status', cams.get())

    def on_disconnect(self):
        logger.info("Web client disconnected")
        
    def on_config_update(self, data):
        logger.info("config update requested: %s" % data)
        emit('config_update', data, namespace='/cam', broadcast=True)
        
    def on_manual_capture(self, data):
        logger.info("manual capture requested: %s" % data)
        emit('manual_capture', data, namespace='/cam', broadcast=True)


