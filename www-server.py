#!flask/bin/python
from yeti.server import app
from yeti.server import www, api

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
