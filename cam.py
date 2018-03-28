#!/usr/bin/env python

import sys, time
sys.path.insert(0, '/home/yeti/cam/')

import yeti.cam

try:
    while True:
        time.sleep(.5)
except KeyboardInterrupt:
    exit()
