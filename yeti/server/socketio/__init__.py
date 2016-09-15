from yeti.server import app
import namespaces
from flask_socketio import SocketIO

socketio = SocketIO(app)

socketio.on_namespace(namespaces.CamEvents('/cam'))
socketio.on_namespace(namespaces.WebEvents('/web'))

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    pass