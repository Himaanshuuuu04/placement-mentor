from bullmq import Queue
from shared.storage import get_minio
from shared.db import get_postgres, init_postgres
import io
import uuid

from shared.config import settings

classify_queue = Queue("document-classify", {"connection": {"host": settings.redis_host, "port": settings.redis_port}})

async def process_document(job, job_token):
    await init_postgres()
    pool = get_postgres()
    minio = get_minio()
    data = job.data
    doc_id = data["doc_id"]
    version = data["version_hash"]
    
    obj = minio.get_object("raw", f"{doc_id}/v{version}/page.md")
    markdown = obj.read().decode('utf-8')
    
    # Basic normalization (boilerplate removal should be here)
    processed = markdown.strip()
    
    processed_bytes = processed.encode('utf-8')
    minio.put_object("processed", f"{doc_id}/v{version}/clean.md", io.BytesIO(processed_bytes), len(processed_bytes))
    
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE document_versions SET s3_processed_uri = $1 WHERE document_id = $2 AND version_hash = $3",
            f"s3://processed/{doc_id}/v{version}/clean.md", uuid.UUID(doc_id), version
        )
        
    await classify_queue.add("classify", {"doc_id": doc_id, "version_hash": version})
