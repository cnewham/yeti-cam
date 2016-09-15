from yeti.server import app
from flask_restful import Api
import v1

api = Api(app)

api.add_resource(v1.CaptureApi, '/api/capture')
api.add_resource(v1.ImageApi, '/api/image') #Depreciated
api.add_resource(v1.ConfigApi, '/api/config')
api.add_resource(v1.StatusApi, '/api/status')
api.add_resource(v1.LogApi, '/api/log')