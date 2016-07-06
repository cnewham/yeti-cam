﻿__author__ = 'chris'
import threading, time, os, sys, signal
from datetime import datetime
from yeti.common import constants, config
from yeti.cam import service, sensors
import camera_v3 as camera

import logging
logger = logging.getLogger(__name__)
global keep_alive

logger.info("Starting yeticam")

def send(filename, event, capture_type):
    try:
        logger.info("Sending image with event %s" % event)
        status = {}
        status[constants.STATUS_EVENT] = event

        #read temperature/humidity values
        for key, value in temp.read().iteritems():
            if value != {}:
                status[key] = value

        status[constants.STATUS_TIME] = datetime.now().isoformat()

        if capture_type == constants.EVENT_TYPE_IMAGE:
            server.post_image(filename, event)
        elif capture_type == constants.EVENT_TYPE_VIDEO:
            server.post_video(filename, event)
        else:
            logger.warning("Unknown capture type")

        server.post_status(status)
        os.remove(filename)
    except Exception:
        logger.exception("An error occurred while attempting to upload to server")

def config_update():
    logger.info( "Checking for config updates")
    try:
        server_configs = server.get_config()

        if server_configs is None or server_configs[constants.CONFIG_VERSION] < config.get(constants.CONFIG_VERSION):
            logger.info("Server config out of date, sending updated cam config")
            server.send_config()
        elif server_configs[constants.CONFIG_VERSION] > config.get(constants.CONFIG_VERSION):
            logger.info("Cam config updating from server")

            config.update(server_configs)
            config.set_status(constants.CONFIG_STATUS_UPDATED)
            server.send_config_status(config.get_status())

            restart_capture() #send restart request
    except ValueError:
        logger.exception("Could not parse response from server")
    except Exception as ex:
        logger.exception("Could not update configs from the server")

def check_config_updates():
    while True:
        config_update()
        time.sleep(config.get(constants.CONFIG_CHECK_INTERVAL_MIN) * constants.SECONDS2MIN)

def capture_timer_image():
    time.sleep(5) #Sleep for 30 seconds on startup then take the first picture
    while True:
        logger.info("Capturing timer image: %i min" % config.get(constants.CONFIG_TIMER_INTERVAL_MIN))

        success = capture.request_image()

        if not success:
            logger.info("Timer image was triggered by the camera was already in use")

        time.sleep(config.get(constants.CONFIG_TIMER_INTERVAL_MIN) * constants.SECONDS2MIN)

#Initialize
capture = camera.CaptureHandler(send)
temp = sensors.Temperature()
server = service.YetiService(config.get(constants.CONFIG_SERVER))

def restart_capture():
    global keep_alive
    keep_alive = True
    capture.stop()

def camera_capture():
    global keep_alive
    keep_alive = True

    while keep_alive:
        try:
            keep_alive = False
            capture.start()
        except Exception:
            logger.exception("Camera capture failed.")

#start all threads and run until a stop signal is detected
camera_capture_thread = threading.Thread(target=camera_capture)
camera_capture_thread.start()

config_update_thread = threading.Thread(target=check_config_updates)
config_update_thread.daemon = True
config_update_thread.start()

timer_capture_thread = threading.Thread(target=capture_timer_image)
timer_capture_thread.daemon = True
timer_capture_thread.start()

def signal_handler(signal, frame):
    logger.warning("Stop signal detected...")
    capture.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

