from flask import Flask
from flask_restful import Api

flask = Flask(__name__)
api = Api(flask)

from app import apis
from app import content

flask.config['UPLOAD_FOLDER'] = 'uploads/'
flask.config['ALLOWED_EXTENSIONS'] = set(['jpg', 'jpeg'])

api.add_resource(apis.ImageApi, '/api/image')
api.add_resource(apis.ConfigAPi, '/api/config')


