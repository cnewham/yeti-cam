__author__ = 'chris'
import threading, time
from yeti.common import constants, config, log
from datetime import datetime
import service
import sensors
import camera

temp = sensors.Temperature()
#server = service.YetiService(config.get(constants.CONFIG_SERVER))

camera.motion_detect()

def send(image, event):
    log.LogInfo(__name__, "Sending image with event %s" % event)
    status = {}
    status[constants.STATUS_EVENT] = event
    status[constants.STATUS_INDOOR_TEMP] = temp.read(constants.STATUS_INDOOR_TEMP)
    status[constants.STATUS_OUTDOOR_TEMP] = temp.read(constants.STATUS_OUTDOOR_TEMP)
    status[constants.STATUS_TIME] = datetime.now().isoformat()

    #if event == constants.EVENT_MOTION:
    #    camera.motion_events += 1

    #status[constants.STATUS_MOTION_EVENTS_24H] = camera.motion_events

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


#config_update_thread = threading.Thread(target=check_config_updates)
#config_update_thread.daemon = True
#config_update_thread.start()

#send("%s/capture.jpg" % config.get(constants.CONFIG_IMAGE_DIR), constants.EVENT_TIMER)


