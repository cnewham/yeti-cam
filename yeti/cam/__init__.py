__author__ = 'chris'
from yeti.common import constants, config, log
from datetime import datetime
import service
import sensors
#import camera

temp = sensors.Temperature()
server = service.YetiService(config.get(constants.CONFIG_SERVER))

#camera.motion_detect(lambda: send)

def send(image, event):
    log.LogInfo(__name__, "Sending image with event %s" % event)
    status = {}
    status[constants.STATUS_EVENT] = event
    status[constants.STATUS_INDOOR_TEMP] = temp.read(constants.STATUS_INDOOR_TEMP)
    status[constants.STATUS_OUTDOOR_TEMP] = temp.read(constants.STATUS_OUTDOOR_TEMP)
    status[constants.STATUS_TIME] = datetime.now().isoformat()
    status[constants.STATUS_MOTION_EVENTS_24H] = 2

    server.post_image(image, status)


def check_config_updates():
    log.LogInfo(__name__, "Checking for config updates")
    configs = server.get_config()

    if configs[constants.CONFIG_VERSION] > config.get(constants.CONFIG_VERSION):
        config.update(configs)

send("test", "timer")

