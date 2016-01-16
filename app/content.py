from app import flask

@flask.route('/')
def index():
    return "Hello, World!"