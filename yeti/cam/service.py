__author__ = 'chris'
import json
import requests
from yeti.common import log

class YetiService:
    def __init__(self, url = 'http://localhost:5000/api/'):
        self.baseUrl = url
        log.LogInfo(__name__, "YetiService starting: " + self.baseUrl)

    def post_image(self, imageBytes, status):
        log.LogInfo(__name__, "Status: %s" % json.dumps(status))

    def get_config(self):
        return requests.get(self.baseUrl + "config")
        log.LogInfo(__name__, "GetConfig")