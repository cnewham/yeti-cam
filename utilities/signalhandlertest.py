#!/usr/bin/env python

import time, signal, sys
import threading


class ShutdownSignalHandler:
    def __init__(self):
        self.subscribers = []
        signal.signal(signal.SIGINT, self._handler)
        signal.signal(signal.SIGTERM, self._handler)

    def _handler(self, signal, frame):
        print "Stop signal detected: %s" % signal
        self.shutdown()

    def subscribe(self, fn):
        self.subscribers.append(fn)

    def shutdown(self):
        print "Shutting down..."
        for subscriber in self.subscribers:
            subscriber()

    def listen(self):
        signal.pause()


class SomeThread:
    def __init__(self):
        self.stopping = False
        self.t = threading.Thread(target=self._worker)
        self.t.start()

    def _worker(self):
        while not self.stopping:
            print "iterating..."
            time.sleep(1)

    def stop(self):
        print "stopping SomeThread"
        self.stopping = True


shutdown_handler = ShutdownSignalHandler()
foo = SomeThread()

shutdown_handler.subscribe(foo.stop)

shutdown_handler.listen()
