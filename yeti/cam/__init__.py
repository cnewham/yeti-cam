__author__ = 'chris'
import threading, time
from yeti.common import constants, config, log
from datetime import datetime
import service
import sensors
import camera

temp = sensors.Temperature()
server = service.YetiService(config.get(constants.CONFIG_SERVER))

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

def config_update():
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

def check_config_updates():
    while True:
        config_update()
        time.sleep(constants.CONFIG_CHECK_UPDATES_MIN)

def capture_timer_image():
    while True:
        image = camera.timer_capture()
        #send(image, constants.EVENT_TIMER)
        time.sleep(constants.CONFIG_TIMER_INTERVAL_MIN)

def scan_motion_image():
    while True:
        if camera.scanMotion():
            image = camera.motion_capture()
            #send(image, constants.EVENT_MOTION)


scan_motion_image()

#config_update_thread = threading.Thread(target=check_config_updates)
#config_update_thread.daemon = True
#config_update_thread.start()

#timer_capture_thread = threading.Thread(target=capture_timer_image)
#timer_capture_thread.daemon = True
#timer_capture_thread.start()

#motion_capture_thread = threading.Thread(target=scan_motion_image)
#motion_capture_thread.daemon = True
#motion_capture_thread.start()





