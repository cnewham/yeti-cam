import threading as threading
import time
from socketIO_client import SocketIO
from socketIO_client.namespaces import LoggingSocketIONamespace


class CamNamespace(LoggingSocketIONamespace):
    def on_connect(self):
        self.emit("hello", "test")
        super(LoggingSocketIONamespace, self).on_connect()

    def on_reconnect(self):
        self.emit("hello", "test")
        super(LoggingSocketIONamespace, self).on_reconnect()


class YetiSocket:
    def __init__(self, host='localhost', port=5001, config_update_callback=None, manual_capture_callback=None):
        self.cam = None
        self.io = None

        self._thread = threading.Thread(target=self._worker, args=(host, port, config_update_callback, manual_capture_callback))
        self._thread.daemon = True
        self._thread.start()

    def _worker(self, host, port, config_update_callback, manual_capture_callback):
        self.io = SocketIO(host, port)
        self.cam = self.io.define(CamNamespace, '/cam')

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

    def connect(self):
        if self.cam:
            self.cam.connect()
        else:
            print "Socket connection not established. Cannot connect"

    def disconnect(self):
        if self.cam and self.io:
            self.cam.disconnect()
            self.io.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.disconnect()


if __name__ == '__main__':
    socket = YetiSocket()

    time.sleep(5)
    socket.disconnect()
