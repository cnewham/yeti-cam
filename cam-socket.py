import threading, time
from socketIO_client import SocketIO, BaseNamespace

class CamNamespace(BaseNamespace):
    def on_connect(self):
        print 'connected to server'

    def on_disconnect(self):
        print 'disconnected from server'

    def on_message(self, data):
        print 'data received: ' + data


class YetiSocket():
    def __init__(self, host='localhost', port=5001, manual_capture_callback=None, status_update_callback=None):
        self.socketIO = SocketIO(host, port)
        self.cam = self.socketIO.define(CamNamespace, '/cam')

        self.cam.on('status_update', self.status_update)
        self.cam.on('manual_capture', self.manual_capture)

        self._thread = threading.Thread(target=self.socketIO.wait)
        self._thread.daemon = False

    def status_update(self, data):
        print 'status update: ' + data

        if self.status_update_callback:
            self.status_update_callback(data)

    def manual_capture(self, data):
        print 'manual capture: ' + data
        
        if self.manual_capture_callback:
            self.manual_capture_callback(data)

    def connect(self):
        self.cam.connect()

    def disconnect(self):
        self.cam.disconnect()
        self.socketIO.disconnect()

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.disconnect()


if __name__ == '__main__':
    socket = YetiSocket('107.22.53.182', 5001)
    time.sleep(1)
    socket.disconnect()
    time.sleep(10)

    
    
