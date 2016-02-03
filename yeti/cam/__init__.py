__author__ = 'chris'
import threading, time, os
from yeti.common import constants, config
from datetime import datetime
import service
import sensors
import camera

import logging
logger = logging.getLogger(__name__)

temp = sensors.Temperature()
server = service.YetiService(config.get(constants.CONFIG_SERVER))
motion = camera.MotionEvents()

motion_events_24h = 0
processing = False
lock = threading.Lock()

def send(image, event):

    try:
        logger.info("Sending image with event %s" % event)
        status = {}
        status[constants.STATUS_EVENT] = event

        #read temperature/humidity values
        for key, value in temp.read().iteritems():
            status[key] = value

        status[constants.STATUS_TIME] = datetime.now().isoformat()
        status[constants.STATUS_MOTION_EVENTS_24H] = motion_events_24h
        server.post_image(image, event)
        server.post_status(status)
        os.remove(image)
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
    except ValueError:
        logger.exception("Could not parse response from server")
    except Exception as ex:
        logger.exception("Could not update configs from the server")

def check_config_updates():
    while True:
        config_update()
        time.sleep(config.get(constants.CONFIG_CHECK_INTERVAL_MIN))

def capture_timer_image():
    global processing
    time.sleep(10)
    while True:
        if not processing:
            with lock:
                processing = True

            logger.info("Capturing timer image: %i min" % config.get(constants.CONFIG_TIMER_INTERVAL_MIN))
            try:
                image = camera.capture_image()
                send(image, constants.EVENT_TIMER)
            except Exception:
                logger.exception("An error occurred when attempting to capture timer image")
            finally:
                with lock:
                    processing = False
        else:
            logger.warning("Timer image could not be captured. Camera already in use")

        time.sleep(config.get(constants.CONFIG_TIMER_INTERVAL_MIN))

def scan_motion_image():
    global processing
    while True:
        sensitivity = config.get(constants.CONFIG_MOTION_SENSITIVITY)
        threshold = config.get(constants.CONFIG_MOTION_THRESHOLD)
        capture_threshold = config.get(constants.CONFIG_MOTION_CAPTURE_THRESHOLD)
        motion_delay = config.get(constants.CONFIG_MOTION_DELAY_SEC)

        try:
            if camera.scanMotion(sensitivity, threshold):
                if motion.enabled():
                    if not processing:
                        with lock:
                            processing = True

                        logger.info("Capturing motion image: threshold=%i sensitivity=%i ......"  % (threshold, sensitivity))
                        image = camera.capture_image()
                        send(image, constants.EVENT_MOTION)

                        with lock:
                            processing = False
                    else:
                        logger.warning("Motion image could not be captured. Camera already in use")
                else:
                    logger.warning("Motion events disabled for %s seconds because threshold (%s) has been exceeded" % (motion_delay, capture_threshold))
                    time.sleep(motion_delay)
        except Exception:
            logger.exception("An error occurred when attempting to capture motion image")
        finally:
            with lock:
                processing = False

config_update_thread = threading.Thread(target=check_config_updates)
config_update_thread.daemon = True
config_update_thread.start()

timer_capture_thread = threading.Thread(target=capture_timer_image)
timer_capture_thread.daemon = True
timer_capture_thread.start()

motion_capture_thread = threading.Thread(target=scan_motion_image)
motion_capture_thread.daemon = True

if config.get(constants.CONFIG_MOTION_ENABLED):
    motion_capture_thread.start()





