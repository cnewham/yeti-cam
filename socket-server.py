#!flask/bin/python
from yeti.server import app
from yeti.server.socketio import socketio

socketio.run(app, host='0.0.0.0', port=5001)