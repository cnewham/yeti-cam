__author__ = 'chris'
import pika,json
import threading

import logging
logger = logging.getLogger(__name__)

class EventHandler:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='events',type='fanout')
        self._thread = None

    def send(self, event, data):
        logger.info("Sending event %s with data %s" % (event,data))
        body = {'event':event,'data':data}
        self.channel.basic_publish(exchange='events',routing_key='',body=json.dumps(body))

    def receive(self, handler):
        def callback(ch, method, properties, body):
            logger.info("Receiving event: %s" % body)
            message = json.loads(body)
            handler(message['event'], message['data'])

        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        self.channel.basic_consume(callback, queue=queue_name,no_ack=True)
        self.channel.queue_bind(exchange='events',queue=queue_name)

        #self.channel.start_consuming()
        self._thread = threading.Thread(target=self.channel.start_consuming)
        self._thread.daemon = True
        self._thread.start()

    def close(self):
        self.connection.close()

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
