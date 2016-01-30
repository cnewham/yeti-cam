__author__ = 'chris'
import json
import requests
from yeti.common import log, config

class YetiService:
    def __init__(self, url = 'http://localhost:5000/api/'):
        self.baseUrl = url
        log.LogInfo(__name__, "YetiService starting: " + self.baseUrl)

    def post_image(self, image):
        log.LogInfo(__name__, "Posting Image: %s" % image)
        try:
            multiple_files = [('images', ('capture.jpg', open(image, 'rb'), 'image/jpg'))]
            r = requests.post(self.baseUrl + "image", files=multiple_files)
            log.LogInfo(__name__, "StatusCode: %s, Text: %s" % (r.status_code, r.text))
        except Exception as ex:
            print type(ex)
            print ex

    def post_status(self, status):
        log.LogInfo(__name__, "Posting Status: %s" % json.dumps(status))
        try:
            r = requests.post(self.baseUrl + "status", json=status)
            log.LogInfo(__name__, "StatusCode: %s, Text: %s" % (r.status_code, r.text))
        except Exception as ex:
            print type(ex)
            print ex

    def get_config(self):
        try:
            log.LogInfo(__name__, "Getting Config")
            r = requests.get(self.baseUrl + "config")
            log.LogInfo(__name__, "StatusCode: %s" % r.status_code)
            configs = json.loads(r.text)
            return configs
        except ValueError as ex:
            log.LogError(__name__, "Could not parse response from server", ex)
            raise ex

    def send_config(self):
        log.LogInfo(__name__, "Updating server configs")
        r = requests.put(self.baseUrl + "config", json=config.get())
        log.LogInfo(__name__, "StatusCode: %s, Text: %s" % (r.status_code, r.text))
