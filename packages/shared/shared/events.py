
from bullmq import Queue
from shared.config import settings

def get_queue(queue_name: str):
    return Queue(queue_name, {"connection": {"host": settings.redis_host, "port": settings.redis_port}})
