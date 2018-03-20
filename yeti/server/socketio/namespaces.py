from flask_socketio import Namespace, emit, send
from flask import request

import logging
logger = logging.getLogger(__name__)

online = {}


class Cam(Namespace):
    def on_connect(self):
        logger.info("Camera (%s) client connected" % request.sid)

    def on_disconnect(self):
        global online
        logger.info("Camera (%s) client disconnected" % request.sid)
        del online[request.sid]
        emit('camera_status', online, namespace='/web', broadcast=True)

    def on_hello(self, name):
        global online
        online[request.sid] = name
        logger.info("Camera %s (%s) said hello" % (name, request.sid))
        emit('camera_status', online, namespace='/web', broadcast=True)

    def on_config_updated(self, data):
        emit('config_updated', data, namespace='/web', broadcast=True)

    def on_manual_capture_result(self, data):
        emit('manual_capture_result', data, namespace='/web', broadcast=True)


class Web(Namespace):
    def on_connect(self):
        logger.info("Web client connected")
        emit('camera_status', {'connected': online})

    def on_disconnect(self):
        logger.info("Web client disconnected")
        
    def on_config_update(self, data):
        logger.info("config update requested: %s" % data)
        emit('config_update', data, namespace='/cam', broadcast=True)
        
    def on_manual_capture(self, data):
        logger.info("manual capture requested: %s" % data)
        emit('manual_capture', data, namespace='/cam', broadcast=True)


