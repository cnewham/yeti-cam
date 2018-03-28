import sys
import signal
import logging

logger = logging.getLogger(__name__)


class ShutdownSignalHandler:
    def __init__(self, subscribers=None):
        self.subscribers = subscribers or []
        signal.signal(signal.SIGINT, self._handler)
        signal.signal(signal.SIGTERM, self._handler)

    def _handler(self, signal, frame):
        logger.warn("Stop signal detected: %s" % signal)
        self.shutdown()

    def subscribe(self, fn):
        self.subscribers.append(fn)

    def shutdown(self):
        logger.warn("Shutting down...")
        for subscriber in self.subscribers:
            subscriber()

        logger.info("Shutdown complete")
        sys.exit(0)
