from bullmq import Queue
import hashlib

from shared.config import settings

embed_queue = Queue("document-embed", {"connection": {"host": settings.redis_host, "port": settings.redis_port}})

async def process_dedup(job, job_token):
    # Level 1 (URL) is handled in DB
    # Level 2 (Hash) implementation logic:
    # Here we simulate checking if content is duplicated.
    data = job.data
    await embed_queue.add("embed", data)
