from yeti.server import app as application
import yeti.server.socketio

socketio.run(app, host='0.0.0.0' port=8080)