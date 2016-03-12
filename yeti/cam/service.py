__author__ = 'chris'
import json
import requests
from yeti.common import config, constants


import logging
logger = logging.getLogger(__name__)

class YetiService:
    def __init__(self, url = 'http://localhost:5000/api/'):
        self.baseUrl = url
        logger.info("YetiService starting: " + self.baseUrl)

    def post_image(self, image, event):
        logger.info("Posting Image: %s" % image)
        multiple_files = [('uploads', (image, open(image, 'rb'), 'image/jpg'))]
        r = requests.post(self.baseUrl + "capture", files=multiple_files, data={"event":event})
        logger.info("StatusCode: %s, Text: %s" % (r.status_code, r.text))

    def post_video(self, video, event):
        logger.info("Posting Video: %s" % video)
        multiple_files = [('uploads', (video, open(video, 'rb'), 'video/h264'))]
        r = requests.post(self.baseUrl + "capture", files=multiple_files, data={"event":event})
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

    def send_config_status(self, status):
        logger.info("Updating server config status")
        r = requests.patch(self.baseUrl + "config", json={'status': status})
        logger.info("StatusCode: %s, Text: %s" % (r.status_code, r.text))
