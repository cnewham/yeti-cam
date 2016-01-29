__author__ = 'chris'
from yeti.common import constants
from yeti.common import log

import config
import service
import sensors
#import camera

temp = sensors.Temperature()
server = service.YetiService(config.get(constants.CONFIG_SERVER))

#temp.read()
#camera.motion_detect(lambda: send)

def send(image, event):
    status = {}
    #TODO: build status object to send with image

    server.post_image(image, status)
    log.LogInfo(__name__, "Sending image with event %s" % event)

def check_config_updates():
    log.LogInfo(__name__, "Checking for config updates")
    configs = server.get_config()

    if configs[constants.CONFIG_VERSION] > config.get(constants.CONFIG_VERSION):
        config.update(configs)

