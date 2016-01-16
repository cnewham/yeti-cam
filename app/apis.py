from flask_restful import Resource

class ImageApi(Resource):
    def get(self):
        return {'hello': 'world'}


class ConfigAPi(Resource):
    def get(self):
        return {'hello': 'world'}