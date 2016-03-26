#!/usr/bin/env python


import picamera, picamera.array
import numpy as np

class MotionDetector(picamera.array.PiMotionAnalysis):
    def __init__(self, camera):
        super(MotionDetector, self).__init__(camera)

    def analyse(self, a):
        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)

        text = ""
        for i in range(0,100,5):

            text += "[%s:%s] " % (i, (a>i).sum())

        camera.annotate_text = text

        #if (a > self.sensitivity).sum() > self.threshold:
        #    logger.debug("Motion Detected!")

seconds = 10
print("Initializing camera")
with picamera.PiCamera() as camera:
    try:
        camera.led = False
        camera.resolution = (800,600)
        camera.framerate = 24
        camera.vflip = False
        camera.hflip = False
        camera.annotate_text_size = 10
        camera.annotate_background = picamera.Color('black')
        camera.annotate_frame_num = True
        camera.awb_mode='horizon'
        camera.exposure_mode='night'
        camera.start_preview()
        print("Recording sample for %s seconds..." % seconds)
        camera.start_recording('motion.h264', format='h264', quality=25, motion_output=MotionDetector(camera))

        camera.wait_recording(seconds)

        camera.stop_recording()
        camera.stop_preview()
    finally:
        print("Closing camera")
        camera.close()
