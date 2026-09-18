
import logging
from pythonjsonlogger import jsonlogger
from asgi_correlation_id import correlation_id

class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id.get() or "unknown"
        return True

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(correlation_id)s %(name)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.addFilter(CorrelationIdFilter())
    return logger
