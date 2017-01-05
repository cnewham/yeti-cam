__author__ = 'chris'
import time
from yeti.server import rabbitmq

def callback(*args):
    print "Received data: %s" % args

queue = rabbitmq.EventHandler()

queue.send('test', {'a':'a','b':'b'})

queue.close()

