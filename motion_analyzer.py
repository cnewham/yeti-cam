#!/usr/bin/env python

import io
import picamera, picamera.array
import numpy as np

FILE_BUFFER = 1048576            # the size of the file buffer (bytes)
REC_RESOLUTION = (1280, 720) # the recording resolution
REC_FRAMERATE = 24           # the recording framerate
REC_SECONDS = 5             # number of seconds to store in ring buffer
REC_BITRATE = 1000000        # bitrate for H.264 encoder

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
        camera.resolution = REC_RESOLUTION
        camera.framerate = REC_FRAMERATE
        camera.vflip = False
        camera.hflip = False
        camera.annotate_text_size = 10
        camera.annotate_background = picamera.Color('black')
        camera.annotate_frame_num = True
        camera.awb_mode='horizon'
        camera.exposure_mode='night'
        camera.start_preview()
        print("Recording sample for %s seconds..." % seconds)
        stream = picamera.PiCameraCircularIO(camera, seconds=REC_SECONDS, bitrate=REC_BITRATE)
        camera.start_recording(stream, format='h264', bitrate=REC_BITRATE, intra_period=REC_FRAMERATE, motion_output=MotionDetector(camera))

        camera.wait_recording(10)

        #Write before motion buffer into file first
        with io.open('motion_test.h264', 'wb') as output:
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

            camera.split_recording(output)
            camera.wait_recording(4)
            camera.stop_recording()

        #stream = picamera.PiCameraCircularIO(camera, seconds=3)
        #camera.split_recording(stream)

        camera.stop_preview()
    finally:
        print("Closing camera")
        camera.close()
