#!/usr/bin/env python

import io
from datetime import datetime, timedelta
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

        self.camera.annotate_text = text

        #if (a > self.sensitivity).sum() > self.threshold:
        #    print("Motion Detected!")

class RGBMotionDetector(picamera.array.PiRGBAnalysis):
    """
    Calculates an average RGB value for each pixel, from a sample of images, and detects motion if there are any changes beyond
    the threshold value
    """
    def __init__(self, camera, handler, sensitivity, threshold, delay=3, sample_size=10):
        super(RGBMotionDetector, self).__init__(camera, size=(320,240))
        self.handler = handler
        self.sensitivity = sensitivity
        self.threshold = threshold
        self.delay = delay
        self.last = datetime.now()
        self.background = None
        self.cache = []
        self.sample_size = sample_size

    def delayed(self):
        return (datetime.now() - timedelta(seconds=self.delay)) < self.last

    def analyse(self, a):

        try:
            current = a.mean(axis=2) #calculate average RGB value for the current frame
            print current.shape

            if self.background is None: #check if we've built a big enough sample to average
                print('building cache')
                self.cache.append(current)
                if len(self.cache) >= self.sample_size:
                    print('calculating background average')
                    sample = np.array(self.cache)
                    print sample.shape
                    self.background = sample.mean(axis=0) #average the background image for comparison to subsequent frames
                    print self.background.shape
                    self.cache = []
                else:
                    return

            print('comparing current image')
            diff = abs(current - self.background)

            print('detecting motion')
            if (diff > self.threshold).sum() > self.sensitivity:
                print('motion detected!')
                self.handler.motion_detected()
                self.last = datetime.now()
                self.background = None
        except Exception as ex:
            print ex
            return

class MotionCallback():
    def motion_detected(self):
        print "Motion Callback called"

def rgb_motion_detector_test():
    seconds = 60
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

            analyzer = RGBMotionDetector(camera, MotionCallback(), 10, 60, sample_size=10)
            camera.start_recording(analyzer, format='rgb', resize=(320,240))

            recording = 0
            while recording <= seconds:
                camera.wait_recording(1)
                recording += 1

            camera.stop_recording()
            camera.stop_preview()
        except Exception as ex:
            print ex
        finally:
            print("Closing camera")
            camera.close()

def capture_sequence(frames=100):
    framerate = 2
    print("Initializing camera")
    with picamera.PiCamera() as camera:
        try:
            camera.led = False
            camera.resolution = (320,240)
            camera.framerate = framerate
            camera.vflip = False
            camera.hflip = False
            camera.awb_mode='horizon'
            camera.exposure_mode='fixedfps'
            camera.start_preview()
            print("Capturing %s frames @ %s frames/sec..." % (frames, framerate))

            camera.start_preview()
            camera.capture_sequence([
                '/home/chris/sequence/image%02d.jpg' % i
                for i in range(frames)
                ])
            camera.stop_preview()

        except Exception as ex:
            print ex
        finally:
            print("Closing camera")
            camera.close()

def circular_buffer_test():
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

#start here
capture_sequence()