#!/usr/bin/env python

__author__ = 'chris'
import threading, time, io
from datetime import datetime, timedelta
import picamera
import picamera.array
import numpy as np
from yeti.common import config, constants

import logging
logger = logging.getLogger(__name__)
FILE_BUFFER = 1048576            # the size of the file buffer (bytes)
REC_SECONDS = 2             # number of seconds to store in ring buffer
REC_BITRATE = 1000000        # bitrate for H.264 encoder
REC_FRAMERATE = 24          #frame rate to capture
camera_lock = threading.Lock()

class MotionEvents:
    def __init__(self):
        self.motion_events = 0
        self.last_motion_event = None

    def enabled(self):
        if not config.get(constants.CONFIG_MOTION_ENABLED):
            return False #motion disabled in configuration

        if self.last_motion_event is None or self.exceeds_motion_capture_delay():
            self.motion_events = 1
            self.last_motion_event = datetime.now()
            return True #doesn't exceed motion capture delay
        elif self.motion_events + 1 <= config.get(constants.CONFIG_MOTION_CAPTURE_THRESHOLD):
            self.motion_events += 1
            self.last_motion_event = datetime.now()
            return True #still within motion capture threshold
        else:
            logger.warning("Motion capture threshold exceeded")
            return False #exceeds motion capture threshold

    def exceeds_motion_capture_delay(self):
        if self.last_motion_event is not None:
            delta_date = datetime.now() - timedelta(seconds=config.get(constants.CONFIG_MOTION_DELAY_SEC))
            return delta_date > self.last_motion_event
        else:
            return True

class MotionDetector(picamera.array.PiMotionAnalysis):
    def __init__(self, camera, handler, sensitivity, threshold, delay=3):
        super(MotionDetector, self).__init__(camera)
        self.handler = handler
        self.sensitivity = sensitivity
        self.threshold = threshold
        self.delay = delay
        self.motion = MotionEvents()
        self.last = datetime.now()

    def delayed(self):
        return (datetime.now() - timedelta(seconds=self.delay)) < self.last

    def analyse(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)

        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion

        if (a > self.sensitivity).sum() > self.threshold and not self.delayed():
            logger.debug("Motion Detected!")

            if self.motion.enabled():
                self.handler.trigger(constants.EVENT_MOTION, constants.EVENT_TYPE_VIDEO)
                self.last = datetime.now()


class EventCaptureHandler:
    def __init__(self, callback=None):
        self.event = None
        self.stopping = False
        self.running = False
        self.callback = callback

    def trigger(self, event, event_type = constants.EVENT_TYPE_IMAGE):
        logger.debug("Attempting to trigger %s event" % event)

        if self.event:
            logger.debug("Already an event waiting to be processed")
            return False

        logger.debug("Triggering %s event" % event)
        self.event = event, event_type
        return True

    def record(self, camera, stream, seconds):
        logger.info("Recording %s event for %s seconds" % (self.event[0], seconds))
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

        return filename

    def capture(self, camera):
        logger.info("Capture %s image" % self.event[0])
        filename = get_filename(config.get(constants.CONFIG_IMAGE_DIR), config.get(constants.CONFIG_IMAGE_PREFIX))

        camera.stop_recording()
        camera.capture(filename, format="jpeg", quality=config.get(constants.CONFIG_IMAGE_QUALITY))

        return filename

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
                stream = picamera.PiCameraCircularIO(camera, seconds=REC_SECONDS)
                camera.start_recording(stream, format='h264', motion_output=MotionDetector(camera, self, sensitivity, threshold))

                while not self.stopping:
                    #logger.debug("checking for events")

                    if self.event:
                        if self.event[1] == constants.EVENT_TYPE_IMAGE:
                            filename = self.capture(camera)
                            logger.info("Continuing capture")
                            stream = picamera.PiCameraCircularIO(camera, seconds=REC_SECONDS)
                            camera.start_recording(stream, format='h264', motion_output=MotionDetector(camera, self, sensitivity, threshold))
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



