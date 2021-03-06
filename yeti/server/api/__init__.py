﻿from yeti.server import app
from flask_restful import Api
import v1, v2
import requests_cache
requests_cache.install_cache("external_requests_cache", backend='sqlite', expire_after=10)

api = Api(app)

# V1 API
api.add_resource(v1.CaptureApi, '/api/capture')
api.add_resource(v1.ImageApi, '/api/image') #Depreciated
api.add_resource(v1.ConfigApi, '/api/config')
api.add_resource(v1.StatusApi, '/api/status')

# V2 API
api.add_resource(v2.CaptureApi, '/api/v2/capture', '/api/v2/capture/<string:name>', endpoint='captureapi.v2')
api.add_resource(v2.MoultrieCaptureApi, '/api/v2/moultrie', endpoint='moultrie.v2')
api.add_resource(v2.ConfigApi, '/api/v2/config', '/api/v2/config/<string:name>', endpoint='configapi.v2')
api.add_resource(v2.StatusApi, '/api/v2/status', '/api/v2/status/<string:name>', endpoint='statusapi.v2')
api.add_resource(v2.WeatherApi, '/api/v2/weather', endpoint='weatherapi.v2')
api.add_resource(v2.CamsApi, '/api/v2/cams', endpoint='camsapi.v2')