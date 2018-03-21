import threading as threading
import time
from socketIO_client import SocketIO, LoggingNamespace


class YetiSocket:
    def __init__(self, host='localhost', port=5001, config_update_callback=None, manual_capture_callback=None):
        self._thread = threading.Thread(target=self._worker, args=(host, port, config_update_callback, manual_capture_callback))
        self._thread.daemon = True
        self._thread.start()
        self.cam = None
        self.io = None

    def _worker(self, host, port, config_update_callback, manual_capture_callback):
        self.io = SocketIO(host, port)
        self.cam = self.io.define(LoggingNamespace, '/cam')

        if config_update_callback:
            self.cam.on('config_update', config_update_callback)

        if manual_capture_callback:
            self.cam.on('manual_capture', manual_capture_callback)

        self.io.wait()

    def config_updated(self, status):
        print "Sending config updated result: %s" % status
        self.cam.emit("config_updated", {"status":status})

    def manual_capture_result(self, result):
        print "Sending manual capture result: %s" % result
        self.cam.emit("manual_capture_result", {"result": result})

    def hello(self):
        print "Sending hello"
        if self.cam:
            self.cam.emit("hello", "test")

    def connect(self):
        if self.cam:
            self.cam.connect()

    def disconnect(self):
        self.cam.disconnect()
        self.io.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.disconnect()

if __name__ == '__main__':
    socket = YetiSocket()

    time.sleep(1)

    socket.hello()

    time.sleep(30)
    socket.disconnect()
