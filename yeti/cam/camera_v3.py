__author__ = 'chris'
import threading, time, io, os
from datetime import datetime, timedelta
import picamera
import motion
from yeti.common import config, constants

import logging
logger = logging.getLogger(__name__)

FILE_BUFFER = 1048576            # the size of the file buffer (bytes)
REC_SECONDS = 2             # number of seconds to store in ring buffer
REC_BITRATE = 1000000        # bitrate for H.264 encoder
REC_FRAMERATE = 24          #frame rate to capture

class YetiPiCamera:
    """
    Facade for picamera. Handles the implementation of YetiCam for use with picamera:
    start() - starts PiCameraCircularIO stream and RGBMotionDetector
    stop() - stops all captures
    wait(seconds) - accesses wait_recording(seconds)
    close() - destroys the picamera instance
    capture() - captures an image to a file. returns filename
    record(seconds) - records the current stream with an additional n seconds to a file. returns filename
    """
    def __init__(self, camera):
        self.camera = camera
        self.buffer = picamera.PiCameraCircularIO(camera, seconds=REC_SECONDS)
        self.__lock__ = threading.Lock()

    def record(self, seconds):
        with self.__lock__:
            logger.info("Recording %s event for %s seconds" % (self.event[0], seconds))
            filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), "recording-", "h264")
            temp = "%s.temp" % filename

            #Split the recording into the output file for the after motion data
            self.camera.split_recording(temp)

            #Write before motion buffer into file            
            with io.open(filename, 'wb') as output:
                with self.buffer.lock:
                    for frame in stream.frames:
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
                with io.open(temp) as input:
                    output.write(input.read()) #TODO: does this output the video correctly?

            os.remove(temp)

            return filename

    def capture(self):
        with self.__lock__:
            logger.info("Capture %s image" % self.event[0])
            self.working = True
            filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), config.get(constants.CONFIG_IMAGE_PREFIX))
            
            #TODO: Camea is using video port for captures. convert this to use the capture port for better quality
            self.camera.capture(filename, format="jpeg", use_video_port=True, quality=config.get(constants.CONFIG_IMAGE_QUALITY))
            
            return filename

    def start(self):
        logger.info("Starting capture")

        sensitivity = config.get(constants.CONFIG_MOTION_SENSITIVITY)
        threshold = config.get(constants.CONFIG_MOTION_THRESHOLD)

        self.camera.resolution = (config.get(constants.CONFIG_IMAGE_WIDTH), config.get(constants.CONFIG_IMAGE_HEIGHT))
        self.camera.framerate = REC_FRAMERATE

        self.camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
        self.camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)

        self.camera.exposure_mode = config.get(constants.CONFIG_IMAGE_EXPOSURE_MODE)
        self.camera.awb_mode = config.get(constants.CONFIG_IMAGE_AWB_MODE)

        self.camera.led = False

        analyzer = motion.RGBMotionDetector(self.camera, self, sensitivity, threshold, sample_size=REC_FRAMERATE * 2)

        self.camera.start_recording(self.buffer, format='h264')
        self.camera.start_recording(analyzer, format='rgb', splitter_port=2, resize=(320,240))

        return recorder

    def wait(self, seconds=1):
        logger.debug('Waiting for %s second(s)' % seconds)
        self.camera.wait_recording(seconds)

    def stop(self):
        logger.info("Stopping capture")
        self.camera.stop_recording(splitter_port=2)
        self.camera.stop_recording()

    def close(self):
        if not self.camera.closed():
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

    def motion_detected(self):
        logger.debug("Motion capture requested")
        if self.working:
            logger.info("Cannot process motion request. Another request is still in progress")
            return False

        if self.motion.enabled():
            self.event = constants.EVENT_MOTION, config.get(constants.CONFIG_MOTION_EVENT_CAPTURE_TYPE)
            return True

        return False

    def request(self):
        logger.debug("Image capture requested")
        if self.working:
            logger.info("Cannot process capture request. Another request is still in progress")
            return False

        self.event = constants.EVENT_TIMER, constants.EVENT_TYPE_IMAGE
        return True

    def start(self):
        if self.running:
            logger.warn("Camera already running")
            return

        logger.info("Starting camera")
        self.event = None
        self.running = True
        self.stopping = False

        with YetiPiCamera(picamera.PiCamera()) as camera:
            try:
                logger.info("Starting capture")
                camera.start()

                while not self.stopping:
                    if self.event:
                        self.working = True
                        if self.event[1] == constants.EVENT_TYPE_IMAGE:
                            filename = camera.capture()
                            logger.info("Continuing capture")
                        elif self.event[1] == constants.EVENT_TYPE_VIDEO:
                            filename = camera.record(3)
                            logger.info("Continuing capture")
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

                    camera.wait()

            except Exception:
                logger.exception("Camera failure has occurred")
            finally:
                logger.info("Stopping camera")
                camera.close()
                self.running = False

    def stop(self):
        if self.running:
            self.stopping = True

            while self.running:
                time.sleep(.5)

def get_filename(path, prefix, ext="jpg"):
    now = datetime.now()
    return "%s/%s%04d%02d%02d-%02d%02d%02d.%s" % ( path, prefix ,now.year, now.month, now.day, now.hour, now.minute, now.second, ext)



