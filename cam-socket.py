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

    def on_config_update(self, *args):
        print 'config update request: ' + args

    def on_event(self, event, *args):
        print 'event %s, args :' % event + args


class YetiSocket():
    def __init__(self, host='127.0.0.1', port=5001, manual_capture_callback=None, config_update_callback=None):
        self.io = SocketIO(host, port)
        self.cam = self.io.define(LoggingNamespace, '/cam')

        self.cam.on('config_update', self.config_update)
        self.cam.on('manual_capture', self.manual_capture)

        self._thread = threading.Thread(target=self.io.wait)
        self._thread.daemon = False

    def config_update(self, *args):
        print 'config update: ' + args

        if self.config_update_callback:
            self.config_update_callback(data)

    def manual_capture(self, *args):
        print 'manual capture: ' + args
        
        if self.manual_capture_callback:
            self.manual_capture_callback(data)

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
    socket = YetiSocket('107.22.53.182', 5001)
    #socket = YetiSocket()
    web = socket.io.define(LoggingNamespace, '/web')
    web.emit("config_update",{"configId":100})
    #web.emit("manual_capture", {})
    
    time.sleep(30)
    socket.disconnect()

    
    
