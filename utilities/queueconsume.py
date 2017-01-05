__author__ = 'chris'
import time
from yeti.server import rabbitmq

def event_callback(event, data):
    print("Event: %s, Data: %s" % (event, data))

queue = rabbitmq.EventHandler()

queue.receive(event_callback)

queue.close()

