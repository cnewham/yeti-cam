from yeti.server import app
import namespaces
from flask_socketio import SocketIO

import logging
logger = logging.getLogger(__name__)

socketio = SocketIO(app)

socketio.on_namespace(namespaces.Cam('/cam'))
socketio.on_namespace(namespaces.Web('/web'))

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    logger.exception('Socket error occurred')