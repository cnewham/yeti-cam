import threading
import time
import os
import logging
from datetime import datetime
import yeti
from yeti.common import constants, config, shutdown
from yeti.cam import service, sensors
import camera_v3 as camera
import motion
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)

logger.info("Starting yeticam as " + yeti.options.name)


def send(filename, event, capture_type):
    try:
        logger.info("Sending image with event %s" % event)
        status = {}
        status[constants.STATUS_EVENT] = event

        # read temperature/humidity values
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


def check_config_updates(request):
    logger.info("Checking for config updates: %s" % request)
    try:
        if not request["name"] == yeti.options.name:
            logger.info("Config request (%s) not for me, ignoring" % request["name"])
            return

        server_configs = server.get_config()

        if server_configs is None or server_configs[constants.CONFIG_VERSION] < config.get(constants.CONFIG_VERSION):
            logger.info("Server config out of date, sending updated cam config")
            server.send_config()
        elif server_configs[constants.CONFIG_VERSION] > config.get(constants.CONFIG_VERSION):
            logger.info("Cam config updating from server")

            config.update(server_configs)
            config.set_status(constants.CONFIG_STATUS_UPDATED)
            server.send_config_status(config.get_status())

            # restart capture to load the most recent configs
            capture.restart()
            socket.config_updated(config.get_status())

    except HTTPError as ex:
        logger.exception(ex)

        if ex.response is not None and ex.response.status_code == 404:
            try:
                logger.info("Attempting to send updated config to server")
                server.send_config()
            except HTTPError as ex:
                logger.exception(ex)
    except ValueError:
        logger.exception("Could not parse response from server")
    except Exception as ex:
        logger.exception("Could not update configs from the server")


def capture_timer_image():
    time.sleep(5) # Sleep for 5 seconds on startup then take the first picture
    while True:
        logger.info("Capturing timer image: %i min" % config.get(constants.CONFIG_TIMER_INTERVAL_MIN))

        success = capture.request()

        if not success:
            logger.info("Timer image was triggered but the camera was already in use")

        time.sleep(config.get(constants.CONFIG_TIMER_INTERVAL_MIN) * constants.SECONDS2MIN)


def capture_manual_image(*args):
    logger.info("Capturing manual image: %s" % args)

    success = capture.request(event=constants.EVENT_MANUAL)

    if not success:
        logger.info("Manual image was triggered but the camera was already in use")

    socket.manual_capture_result(success)


def capture_motion_image(detected):
    logger.info("Motion sensor change: %s" % detected)

    if detected and motion_events.enabled():
        success = capture.motion_detected()
    else:
        return

    if not success:
        logger.info("Motion image was triggered but the camera was already in use")


# Initialize
motion_events = motion.MotionEvents()
motion_sensors = sensors.Motion(capture_motion_image)

capture = camera.CaptureHandler(send)
temp = sensors.Temperature()
server = service.YetiService(config.get(constants.CONFIG_SERVER))
socket = service.YetiSocket(config.get(constants.CONFIG_SOCKET_HOST), config.get(constants.CONFIG_SOCKET_PORT),
                            config_update_callback=check_config_updates, manual_capture_callback=capture_manual_image)

# check for config updates from the server
check_config_updates({"version": "current", "name": yeti.options.name})

# start all threads and run until a stop signal is detected
capture.start()

timer_capture_thread = threading.Thread(target=capture_timer_image)
timer_capture_thread.daemon = True
timer_capture_thread.start()


# shutdown routine
shutdown_handler = shutdown.ShutdownSignalHandler([socket.disconnect, capture.stop])
