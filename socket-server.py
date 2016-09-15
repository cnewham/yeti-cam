#!flask/bin/python
from yeti.server import app
from yeti.server import socketio

app.run(host='0.0.0.0', port=5001)