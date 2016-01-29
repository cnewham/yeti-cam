__author__ = 'chris'
from yeti.common import log

class YetiService:
    def __init__(self, url = 'http://localhost:5000/api/'):
        self.baseUrl = url
        log.LogInfo(__name__, "YetiService starting: " + self.baseUrl)

    def post_image(self, imageBytes, status):
        log.LogInfo(__name__, "PostImage")

    def get_config(self):
        log.LogInfo(__name__, "GetConfig")