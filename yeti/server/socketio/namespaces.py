from flask_socketio import Namespace, emit

class CamEvents(Namespace):
    def on_connect():
        pass

    def on_disconnect():
        pass

    def on_my_event(data):
        emit('my_response', data)

class WebEvents(Namespace):
    def on_connect():
        pass

    def on_disconnect():
        pass

    def on_my_event(data):
        emit('my_response', data)