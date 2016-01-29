__author__ = 'chris'
from yeti.common import log

class YetiService:
    def __init__(self, url = 'http://localhost:5000/api/'):
        self.baseUrl = url
        log.LogInfo(__name__, "YetiService starting: " + self.baseUrl)

    def PostImage(self, imageBytes, status):
        log.LogInfo(__name__, "PostImage")

    def GetConfig(self):
        log.LogInfo(__name__, "GetConfig")