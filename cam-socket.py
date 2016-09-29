import threading, time
from socketIO_client import SocketIO, BaseNamespace, LoggingNamespace

import logging
logging.basicConfig(level=logging.INFO,format="%(name)-12s: %(levelname)-8s %(message)s")

class CamNamespace(BaseNamespace):
    def on_connect(self):
        print 'connected to server'

    def on_disconnect(self):
        print 'disconnected from server'

    def on_message(self, data):
        print 'data received: ' + data


class YetiSocket():
    def __init__(self, host='localhost', port=5001):
        self.io = SocketIO(host, port)
        self.cam = self.io.define(CamNamespace, '/cam')

        self.cam.on('config_update', self.config_update)
        self.cam.on('manual_capture', self.manual_capture)

        self._thread = threading.Thread(target=self.io.wait)
        self._thread.daemon = True
        self._thread.start()

    def send(self, event, data):
        self.cam.emit(event, data)

    def config_update(self, data):
        print 'config update: %s' % data

    def manual_capture(self, data):
        print 'manual capture: ' + data
        
    def connect(self):
        self.cam.connect()

    def disconnect(self):
        self.cam.disconnect()
        self.io.disconnect()

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.disconnect()


if __name__ == '__main__':
    socket = YetiSocket('107.22.53.182', 8080)
    #socket = YetiSocket()

    time.sleep(30)
    socket.disconnect()

    
    
