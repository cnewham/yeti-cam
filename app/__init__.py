from flask import Flask
from flask_restful import Api

flask = Flask(__name__)
api = Api(flask)

from app import apis
from app import content

api.add_resource(apis.ImageApi, '/api/image')
api.add_resource(apis.ConfigAPi, '/api/config')


