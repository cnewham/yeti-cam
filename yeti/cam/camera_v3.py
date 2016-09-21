__author__ = 'chris'
import threading, time, io, os, shutil
from datetime import datetime, timedelta
import picamera
import motion
from yeti.common import config, constants

import logging
logger = logging.getLogger(__name__)

class YetiPiCamera:
    """
    Facade for picamera for use with yeti-cam:
    start() - starts PiCameraCircularIO stream and RGBMotionDetector
    stop() - stops all captures
    wait(seconds) - accesses wait_recording(seconds)
    close() - destroys the picamera instance
    capture() - captures an image to a file. returns filename
    record(seconds) - records the current stream with an additional n seconds to a file. returns filename
    """
    def __init__(self, camera, handler):
        self.camera = camera
        self.handler = handler
        self.buffer = picamera.PiCameraCircularIO(camera, seconds=3)
        self.__lock__ = threading.Lock()

    def record(self, seconds):
        with self.__lock__:
            logger.info("Recording event for %s seconds" % seconds)
            filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), "recording-", "h264")
            temp = "%s.temp" % filename

            #Split the recording into the output file for the after motion data
            self.camera.split_recording(temp)

            #Write before motion buffer into file            
            with io.open(filename, 'wb') as output:
                with self.buffer.lock:
                    for frame in self.buffer.frames:
                        if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                            self.buffer.seek(frame.position)
                            break
                    while True:
                        buf = self.buffer.read1()
                        if not buf:
                            break
                        output.write(buf)

                    self.buffer.seek(0)
                    self.buffer.truncate()

            #split the recording back into the circular stream
            self.camera.wait_recording(seconds)
            self.camera.split_recording(self.buffer)

            #stitch the 2 streams together and remove the temp file
            with io.open(filename, 'ab') as output:
                with io.open(temp, 'rb') as t:
                    output.write(t.read())

            os.remove(temp)

            return filename

    def capture(self):
        with self.__lock__:
            logger.info("Capture image")
            filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), config.get(constants.CONFIG_IMAGE_PREFIX))
            
            self.stop()
            self.camera.resolution = (config.get(constants.CONFIG_IMAGE_WIDTH), config.get(constants.CONFIG_IMAGE_HEIGHT))
            self.camera.capture(filename, format="jpeg", quality=config.get(constants.CONFIG_IMAGE_QUALITY))
            self.start()

            return filename

    def start(self):
        logger.info("Starting capture")

        sensitivity = config.get(constants.CONFIG_MOTION_SENSITIVITY)
        threshold = config.get(constants.CONFIG_MOTION_THRESHOLD)
        percent_change_max = config.get(constants.CONFIG_MOTION_PERCENT_CHANGE_MAX)

        self.camera.resolution = (1280, 720)
        self.camera.framerate = 2

        self.camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
        self.camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)

        self.camera.exposure_mode = config.get(constants.CONFIG_IMAGE_EXPOSURE_MODE)
        self.camera.awb_mode = config.get(constants.CONFIG_IMAGE_AWB_MODE)

        self.camera.led = False

        analyzer = motion.SimpleGaussMotionDetector(self.camera, self.handler, sensitivity, threshold, percent_change_max = percent_change_max)

        self.camera.start_recording(self.buffer, format='h264')
        self.camera.start_recording(analyzer, format='rgb', splitter_port=2, resize=(320,240))

    def wait(self, seconds=1.0):
        self.camera.wait_recording(seconds)

    def stop(self):
        logger.info("Stopping capture")
        self.camera.stop_recording(splitter_port=2)
        self.camera.stop_recording()

    def close(self):
        if not self.camera.closed:
            logger.info('Cleaning up camera')
            self.camera.close()

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.camera.close()
        
class CaptureHandler:
    """
    Handles picamera instance and manages events that are requested.
    Callback should be a function with parameters 
    callback(filename, event, capture_type)
    ..filename = the name of the capture file
    ..event = the name of the event (i.e. motion, timer, manual, etc...)
    ..capture_type = the type of capture - image or video
    """
    def __init__(self, callback=None):
        self.event = None
        self.stopping = False
        self.running = False
        self.working = False
        self.callback = callback
        self.motion = motion.MotionEvents()
        self.t = None

    def _worker(self):
        if self.running:
            logger.warn("Camera already running")
            return

        logger.info("Starting camera")
        self.event = None
        self.running = True
        self.stopping = False

        with YetiPiCamera(picamera.PiCamera(), self) as camera:
            try:
                camera.start()

                while not self.stopping:
                    if self.event:
                        self.working = True
                        if self.event[1] == constants.EVENT_TYPE_IMAGE:
                            filename = camera.capture()
                        elif self.event[1] == constants.EVENT_TYPE_VIDEO:
                            filename = camera.record(3)
                        else:
                            logger.warning("Unknown event capture type: %s" % self.event[1])
                            self.event = None
                            self.working = False
                            continue

                        if filename and self.callback:
                            self.callback(filename, *self.event)
                        else:
                            logger.warning("Capture did not complete successfully")

                        self.event = None
                        self.working = False

                    camera.wait(.5)

            except Exception:
                logger.exception("Camera failure has occurred")
            finally:
                logger.info("Stopping camera")
                camera.close()
                self.running = False

    def motion_detected(self):
        logger.debug("Motion capture requested")
        if self.working:
            logger.info("Cannot process motion request. Another request is still in progress")
            return False

        if self.motion.enabled():
            self.event = constants.EVENT_MOTION, config.get(constants.CONFIG_MOTION_EVENT_CAPTURE_TYPE)
            return True

        return False

    def request(self, event=constants.EVENT_TIMER, event_type=constants.EVENT_TYPE_IMAGE):
        logger.debug("Image capture requested")
        if self.working:
            logger.info("Cannot process capture request. Another request is still in progress")
            return False

        self.event = event, event_type
        return True

    def start(self):
        self.t = threading.Thread(target=self._worker)
        self.t.start()

    def stop(self):
        if self.running:
            self.stopping = True

            while self.running:
                time.sleep(.5)

    def restart(self):
        self.stop()
        self.start()

def get_filename(path, prefix, ext="jpg"):
    now = datetime.now()
    return "%s/%s%04d%02d%02d-%02d%02d%02d.%s" % ( path, prefix ,now.year, now.month, now.day, now.hour, now.minute, now.second, ext)



