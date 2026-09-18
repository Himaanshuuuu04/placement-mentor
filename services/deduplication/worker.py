from bullmq import Queue
import hashlib

embed_queue = Queue("document-embed", {"connection": {"host": "redis", "port": 6379}})

async def process_dedup(job, job_token):
    # Level 1 (URL) is handled in DB
    # Level 2 (Hash) implementation logic:
    # Here we simulate checking if content is duplicated.
    data = job.data
    await embed_queue.add("embed", data)
