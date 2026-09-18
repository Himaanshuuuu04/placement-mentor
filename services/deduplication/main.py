import asyncio
from bullmq import Worker
from shared.config import settings
from worker import process_dedup

async def main():
    worker = Worker("document-deduplicate", process_dedup, {"connection": {"host": settings.redis_host, "port": settings.redis_port}})
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
