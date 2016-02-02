__author__ = 'chris'
import json
import requests
from yeti.common import config


import logging
logger = logging.getLogger(__name__)

class YetiService:
    def __init__(self, url = 'http://localhost:5000/api/'):
        self.baseUrl = url
        logger.info("YetiService starting: " + self.baseUrl)

    def post_image(self, image):
        logger.info("Posting Image: %s" % image)
        multiple_files = [('images', (image, open(image, 'rb'), 'image/jpg'))]
        r = requests.post(self.baseUrl + "image", files=multiple_files)
        logger.info("StatusCode: %s, Text: %s" % (r.status_code, r.text))

    def post_status(self, status):
        logger.info("Posting Status: %s" % json.dumps(status))
        r = requests.post(self.baseUrl + "status", json=status)
        logger.info("StatusCode: %s, Text: %s" % (r.status_code, r.text))

    def get_config(self):
        logger.info("Getting Config")
        r = requests.get(self.baseUrl + "config")
        logger.info("StatusCode: %s" % r.status_code)
        configs = json.loads(r.text)
        return configs

    def send_config(self):
        logger.info("Updating server configs")
        r = requests.put(self.baseUrl + "config", json=config.get())
        logger.info("StatusCode: %s, Text: %s" % (r.status_code, r.text))
