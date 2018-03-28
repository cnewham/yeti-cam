import sys
import signal
import logging

logger = logging.getLogger(__name__)


class ShutdownSignalHandler:
    def __init__(self, handlers=None):
        self.handlers = handlers or []
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        logger.warn("Stop signal detected: %s" % signal)
        self.shutdown()

    def handle(self, fn):
        self.handlers.append(fn)

    def shutdown(self):
        logger.warn("Shutting down...")
        for handler in self.handlers:
            try:
                handler()
            except Exception:
                logger.exception("Failed to execute shutdown handler function")

        logger.info("Shutdown complete")
        sys.exit(0)
