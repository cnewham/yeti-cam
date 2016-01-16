from app import flask
from flask import render_template

@flask.route('/')
def index():
    try:
        return render_template('viewer.html')
    except Exception as ex:
            print type(ex)
            print ex
            return 500