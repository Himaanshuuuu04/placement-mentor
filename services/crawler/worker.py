from bullmq import Queue
from shared.storage import get_minio
from shared.db import get_postgres, init_postgres
import uuid
import httpx
import json
import io

process_queue = Queue("document-process", {"connection": {"host": "redis", "port": 6379}})

async def process_fetch(job, job_token):
    await init_postgres()
    pool = get_postgres()
    minio = get_minio()
    data = job.data
    url = data["url"]
    
    # communicate with Crawl4AI Docker service via HTTP
    try:
        async with httpx.AsyncClient() as client:
            # According to standard Crawl4AI API
            resp = await client.post("http://crawl4ai:11225/crawl", json={"url": url})
            if resp.status_code == 200:
                result = resp.json()
                html = result.get('html', '')
                markdown = result.get('markdown', '')
                
                doc_id = str(uuid.uuid4())
                version_hash = str(uuid.uuid4()) # simplified hash
                
                # store raw
                minio.put_object("raw", f"{doc_id}/v{version_hash}/page.html", io.BytesIO(html.encode()), len(html))
                minio.put_object("raw", f"{doc_id}/v{version_hash}/page.md", io.BytesIO(markdown.encode()), len(markdown))
                
                async with pool.acquire() as conn:
                    # Update DB
                    await conn.execute(
                        "INSERT INTO documents (id, source_id, canonical_url, status) VALUES ($1, $2, $3, 'PROCESSED') ON CONFLICT (canonical_url) DO NOTHING",
                        uuid.UUID(doc_id), uuid.UUID(data["source_id"]), url
                    )
                    await conn.execute(
                        "INSERT INTO document_versions (document_id, version_hash, s3_raw_uri) VALUES ($1, $2, $3)",
                        uuid.UUID(doc_id), version_hash, f"s3://raw/{doc_id}/v{version_hash}/page.md"
                    )
                
                await process_queue.add("process", {"doc_id": doc_id, "version_hash": version_hash})
    except Exception as e:
        print(f"Crawl error for {url}: {e}")
