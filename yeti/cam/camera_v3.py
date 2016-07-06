__author__ = 'chris'
import threading, time, io, os
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
            self.event = constants.EVENT_MOTION, config.get(constants.CONFIG_MOTION_EVENT_CAPTURE_TYPE)
            return True

        return False

    def request_image(self):
        logger.debug("Image capture requested")
        if self.working:
            return False

        self.event = constants.EVENT_TIMER, constants.EVENT_TYPE_IMAGE
        return True

    def record(self, camera, stream, seconds):
        with camera_lock:
            if self.working:
                return

            logger.info("Recording %s event for %s seconds" % (self.event[0], seconds))
            self.working = True
            filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), "recording-", "h264")
            before = "%s-before" % filename
            after = "%s-after" % filename

            #Split the recording into the output file for the after motion data
            camera.split_recording(after, splitter_port=1)

            #Write before motion buffer into file            
            with io.open(before, 'wb') as output:
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

            #split the recording back into the circular stream
            camera.wait_recording(seconds, splitter_port=1)
            camera.split_recording(stream, splitter_port=1)

            #stitch the 2 streams together and remove the temp files
            files = [before, after]
            with io.open(filename, 'wb') as output:
                for file in files:
                    with io.open(file) as input:
                        with input.lock:
                            for frame in input.frames:
                                if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                                    input.seek(frame.position)
                                    break
                            while True:
                                buf = input.read1()
                                if not buf:
                                    break
                                output.write(buf)
                os.remove(file)

            self.working = False
            return filename

    def capture(self, camera):
        with camera_lock:
            if self.working:
                return

            logger.info("Capture %s image" % self.event[0])
            self.working = True
            filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), config.get(constants.CONFIG_IMAGE_PREFIX))
        
            camera.capture(filename, format="jpeg", use_video_port=True, quality=config.get(constants.CONFIG_IMAGE_QUALITY))

            self.working = False
            return filename

    def start_capture(self, camera):
        logger.info("Starting capture")

        sensitivity = config.get(constants.CONFIG_MOTION_SENSITIVITY)
        threshold = config.get(constants.CONFIG_MOTION_THRESHOLD)

        camera.resolution = (config.get(constants.CONFIG_IMAGE_WIDTH), config.get(constants.CONFIG_IMAGE_HEIGHT))
        camera.framerate = REC_FRAMERATE

        camera.vflip = config.get(constants.CONFIG_IMAGE_VFLIP)
        camera.hflip = config.get(constants.CONFIG_IMAGE_HFLIP)

        camera.exposure_mode = config.get(constants.CONFIG_IMAGE_EXPOSURE_MODE)
        camera.awb_mode = config.get(constants.CONFIG_IMAGE_AWB_MODE)

        camera.led = False

        recorder = picamera.PiCameraCircularIO(camera, seconds=REC_SECONDS)
        analyzer = motion.RGBMotionDetector(camera, self, sensitivity, threshold, sample_size=REC_FRAMERATE * 2)

        camera.start_recording(recorder, format='h264', splitter_port=1)
        camera.start_recording(analyzer, format='rgb', splitter_port=2, resize=(320,240))

        return recorder

    def stop_capture(self, camera):
        camera.stop_recording(splitter_port=2)
        camera.stop_recording(splitter_port=1)
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
                logger.info("Starting capture")
                stream = self.start_capture(camera)

                while not self.stopping:
                    if self.event:
                        if self.event[1] == constants.EVENT_TYPE_IMAGE:
                            filename = self.capture(camera)
                            logger.info("Continuing capture")
                        elif self.event[1] == constants.EVENT_TYPE_VIDEO:
                            filename = self.record(camera, stream, 3)
                            logger.info("Continuing capture")
                        else:
                            logger.warning("Unknown event capture type: %s" % self.event[1])
                            self.event = None
                            continue

                        if filename and self.callback:
                            self.callback(filename, *self.event)
                        else:
                            logger.warning("Capture did not complete successfully")

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



