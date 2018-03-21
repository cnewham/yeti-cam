import json
import requests
import yeti
from yeti.common import config
import threading
from socketIO_client import SocketIO, LoggingNamespace

import logging
logger = logging.getLogger(__name__)


class YetiService:
    def __init__(self, url='http://localhost:5000/api/v2/'):
        self.baseUrl = url
        logger.info("YetiService starting: " + self.baseUrl)

    def post_image(self, image, event):
        logger.info("Posting Image: %s" % image)
        multiple_files = [('uploads', (image, open(image, 'rb'), 'image/jpg'))]
        r = requests.post(self.baseUrl + "capture/" + yeti.options.name, files=multiple_files, data={"event": event})
        logger.info("StatusCode: %s, Text: %s" % (r.status_code, r.text))

    def post_video(self, video, event):
        logger.info("Posting Video: %s" % video)
        multiple_files = [('uploads', (video, open(video, 'rb'), 'video/h264'))]
        r = requests.post(self.baseUrl + "capture/" + yeti.options.name, files=multiple_files, data={"event": event})
        logger.info("StatusCode: %s, Text: %s" % (r.status_code, r.text))

    def post_status(self, status):
        logger.info("Posting Status: %s" % json.dumps(status))
        r = requests.post(self.baseUrl + "status/" + yeti.options.name, json=status)
        logger.info("StatusCode: %s, Text: %s" % (r.status_code, r.text))

    def get_config(self):
        logger.info("Getting Config")
        r = requests.get(self.baseUrl + "config/" + yeti.options.name)
        logger.info("StatusCode: %s" % r.status_code)
        configs = json.loads(r.text)
        return configs

    def send_config(self):
        logger.info("Updating server configs")
        r = requests.put(self.baseUrl + "config/" + yeti.options.name, json=config.get())
        logger.info("StatusCode: %s, Text: %s" % (r.status_code, r.text))

    def send_config_status(self, status):
        logger.info("Updating server config status")
        r = requests.patch(self.baseUrl + "config/" + yeti.options.name, json={'status': status})
        logger.info("StatusCode: %s, Text: %s" % (r.status_code, r.text))


class YetiSocket:
    def __init__(self, host='localhost', port=5001, config_update_callback=None, manual_capture_callback=None):
        self.cam = None
        self.io = None

        self._thread = threading.Thread(target=self._worker, args=(host, port, config_update_callback, manual_capture_callback))
        self._thread.daemon = True
        self._thread.start()

    def _worker(self, host, port, config_update_callback, manual_capture_callback):
        self.io = SocketIO(host, port)
        self.cam = self.io.define(LoggingNamespace, '/cam')

        if config_update_callback:
            self.cam.on('config_update', config_update_callback)

        if manual_capture_callback:
            self.cam.on('manual_capture', manual_capture_callback)

        self.hello()

        self.io.wait()

    def config_updated(self, status):
        logger.info("Sending config updated result: %s" % status)
        self.cam.emit("config_updated", {"status":status})

    def manual_capture_result(self, result):
        logger.info("Sending manual capture result: %s" % result)
        self.cam.emit("manual_capture_result", {"result": result})

    def hello(self):
        logger.info("Sending hello")
        if self.cam:
            self.cam.emit("hello", yeti.options.name)
        else:
            logger.error("Socket connection not established. Cannot send hello")

    def connect(self):
        if self.cam:
            self.cam.connect()
        else:
            logger.error("Socket connection not established. Cannot connect")

    def disconnect(self):
        if self.cam and self.io:
            self.cam.disconnect()
            self.io.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.disconnect()
