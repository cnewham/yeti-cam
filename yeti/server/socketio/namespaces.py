from flask_socketio import Namespace, emit, send

import logging
logger = logging.getLogger(__name__)

online = False

class Cam(Namespace):
    def on_connect(self):
        global online
        logger.info("Camera client connected")
        online = True
        emit('camera_status', {'connected': True }, namespace='/web')

    def on_disconnect(self):
        global online
        logger.info("Camera client disconnected")
        online = False
        emit('camera_status', {'connected': False }, namespace='/web')

    def on_status_update(self, data):
        emit('status_update', data, namespace='/web')

    def on_camera_capture(self, data):
        emit('camera_capture', data, namespace='/web')

class Web(Namespace):
    def on_connect(self):
        logger.info("Web client connected")
        emit('camera_status', {'connected': online })

    def on_disconnect(self):
        logger.info("Web client disconnected")
        
    def on_config_update(self):
        send('config_update', namespace='/cam')
        
    def on_manual_capture(self):
        send('manual_capture', namespace='/cam')

