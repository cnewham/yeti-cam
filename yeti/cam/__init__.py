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

    server.post_image(image)
    server.post_status(status)

def check_config_updates():
    log.LogInfo(__name__, "Checking for config updates")
    try:
        server_configs = server.get_config()

        if server_configs is None or server_configs[constants.CONFIG_VERSION] < config.get(constants.CONFIG_VERSION):
            log.LogInfo(__name__, "Server config out of date, sending updated cam config")
            server.send_config()
        elif server_configs[constants.CONFIG_VERSION] > config.get(constants.CONFIG_VERSION):
            log.LogInfo(__name__, "Cam config updating from server")
            config.update(server_configs)
    except ValueError:
        return
    except Exception as ex:
        log.LogError(__name__, "Could not update configs from the server", ex)

check_config_updates()
send("%s/capture.jpg" % config.get(constants.CONFIG_IMAGE_DIR), "timer")

