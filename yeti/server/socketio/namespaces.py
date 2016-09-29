from flask_socketio import Namespace, emit, send

import logging
logger = logging.getLogger(__name__)

online = False

class Cam(Namespace):
    def on_connect(self):
        global online
        logger.info("Camera client connected")
        online = True
        emit('config_update', {})
        emit('camera_status', {'connected': True }, namespace='/web', broadcast=True)

    def on_disconnect(self):
        global online
        logger.info("Camera client disconnected")
        online = False
        emit('camera_status', {'connected': False }, namespace='/web', broadcast=True)

    def on_alert(self, data):
        #TODO: Do stuff on the server when there's an alert
        emit('alert', data, namespace='/web', broadcast=True)

    def on_config_updated(self, data):
        emit('config_updated', data, namespace='/web', broadcast=True)

    def on_manual_capture_result(self, data):
        emit('manual_capture_result', data, namespace='/web', broadcast=True)

class Web(Namespace):
    def on_connect(self):
        logger.info("Web client connected")
        emit('camera_status', {'connected': online })

    def on_disconnect(self):
        logger.info("Web client disconnected")
        
    def on_config_update(self, data):
        logger.info("config update requested: %s" % data)
        emit('config_update', data, namespace='/cam', broadcast=True)
        
    def on_manual_capture(self, data):
        logger.info("manual capture requested: %s" % data)
        emit('manual_capture', data, namespace='/cam', broadcast=True)


