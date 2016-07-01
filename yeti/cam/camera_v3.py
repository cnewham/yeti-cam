__author__ = 'chris'
import threading, time, io
from datetime import datetime, timedelta
from yeti.cam import motion
import picamera
from yeti.common import config, constants

import logging
logger = logging.getLogger(__name__)

camera_lock = threading.Lock()

FILE_BUFFER = 1048576            # the size of the file buffer (bytes)
REC_SECONDS = 2             # number of seconds to store in ring buffer
REC_BITRATE = 1000000        # bitrate for H.264 encoder
REC_FRAMERATE = 24          #frame rate to capture

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
            return False

        if self.motion.enabled():
            #TODO: configuration to determine if it should be image or video
            self.event = constants.EVENT_MOTION, constants.EVENT_TYPE_VIDEO
            return True

        return False

    def request_capture(self):
        logger.debug("Image capture requested")
        if self.working:
            return False

        self.event = constants.EVENT_TIMER, constants.EVENT_TYPE_IMAGE
        return True

    def record(self, camera, stream, seconds):
        #TODO: Fix this function to immediately split_recording to the file and stitch the stream to the beginning.
        #BUG: There is a gap created during capture between the stream writing to disk and the recording is split
        with camera_lock:
            if self.working:
                return

            logger.info("Recording %s event for %s seconds" % (self.event[0], seconds))
            self.working = True
            filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), "recording-", "h264")

            with io.open(filename, 'wb') as output:
                #Write before motion buffer into file first
                with stream.lock:
                    for frame in stream.frames:
                        if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                            stream.seek(frame.position)
                            break
                    while True:
                        buf = stream.read1()
                        if not buf:
                            break
                        output.write(buf)

                    stream.seek(0)
                    stream.truncate()

                #Split the recording into the output file to append motion recording
                camera.split_recording(output)
                camera.wait_recording(seconds)

                #split the recording back into the circular stream
                camera.split_recording(stream)

            self.working = False
            return filename

    def capture(self, camera):
        with camera_lock:
            if self.working:
                return

            logger.info("Capture %s image" % self.event[0])
            self.working = True
            filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), config.get(constants.CONFIG_IMAGE_PREFIX))
        
            camera.capture(filename, format="jpeg", quality=config.get(constants.CONFIG_IMAGE_QUALITY))

            self.working = False
            return filename

    def start_capture(camera):
        logger.info("Starting capture")
        recorder = picamera.PiCameraCircularIO(camera, seconds=REC_SECONDS)
        analyzer = motion.RGBMotionDetector(self, sensitivity, threshold)

        camera.start_recording(recorder, format='h264')
        camera.start_recording(analyzer, format='rgb', splitter_port=1)

        return recorder

    def stop_capture(camera):
        camera.stop_recording(splitter_port=1)
        camera.stop_recording()
        logger.info("Stopping capture")

    def start(self):
        if self.running:
            logger.warn("Camera already running")
            return

        logger.info("Starting camera")
        self.event = None
        self.running = True
        self.stopping = False
        with picamera.PiCamera() as camera:
            try:
                sensitivity = config.get(constants.CONFIG_MOTION_SENSITIVITY)
                threshold = config.get(constants.CONFIG_MOTION_THRESHOLD)

                camera.resolution = (config.get(constants.CONFIG_IMAGE_WIDTH), config.get(constants.CONFIG_IMAGE_HEIGHT))
                camera.framerate = REC_FRAMERATE

                camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
                camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)

                camera.exposure_mode = config.get(constants.CONFIG_IMAGE_EXPOSURE_MODE)
                camera.awb_mode = config.get(constants.CONFIG_IMAGE_AWB_MODE)

                camera.led = False

                logger.info("Starting capture")
                stream = self.start_capture(camera)

                while not self.stopping:
                    if self.event:
                        if self.event[1] == constants.EVENT_TYPE_IMAGE:
                            self.stop_capture(camera)
                            filename = self.capture(camera)
                            logger.info("Continuing capture")
                            stream = self.start_capture(camera)                          
                        elif self.event[1] == constants.EVENT_TYPE_VIDEO:
                            filename = self.record(camera, stream, 3)
                            logger.info("Continuing capture")
                        else:
                            logger.warning("Unknown event capture type: %s" % self.event[1])
                            self.event = None
                            continue

                        if self.callback:
                            self.callback(filename, *self.event)

                        self.event = None

                    time.sleep(1)

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

    def restart(self):
        logger.info("Restarting camera")
        self.stop()
        self.start()

def get_filename(path, prefix, ext="jpg"):
    now = datetime.now()
    return "%s/%s%04d%02d%02d-%02d%02d%02d.%s" % ( path, prefix ,now.year, now.month, now.day, now.hour, now.minute, now.second, ext)



