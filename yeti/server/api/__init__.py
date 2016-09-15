from yeti.server import app
from flask_restful import Api
import apis

api = Api(app)

api.add_resource(apis.CaptureApi, '/api/capture')
api.add_resource(apis.ImageApi, '/api/image') #Depreciated
api.add_resource(apis.ConfigApi, '/api/config')
api.add_resource(apis.StatusApi, '/api/status')
api.add_resource(apis.LogApi, '/api/log')