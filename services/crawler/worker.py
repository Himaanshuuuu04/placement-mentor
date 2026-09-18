from bullmq import Queue
from shared.storage import get_minio
from shared.db import get_postgres, init_postgres
import uuid
import httpx
import json
import io
import os

from shared.config import settings

process_queue = Queue("document-process", {"connection": {"host": settings.redis_host, "port": settings.redis_port}})

async def process_fetch(job, job_token):
    await init_postgres()
    pool = get_postgres()
    minio = get_minio()
    data = job.data
    url = data["url"]
    
    try:
        async with httpx.AsyncClient() as client:
            crawl_url = os.environ.get("CRAWL4AI_URL", "http://crawl4ai:11225/crawl")
            try:
                resp = await client.post(crawl_url, json={"url": url}, timeout=15.0)
                if resp.status_code == 200:
                    result = resp.json()
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]
                    html = result.get('html') or ''
                    markdown = result.get('markdown') or ''
                else:
                    raise Exception(f"Crawl4AI status {resp.status_code}")
            except Exception as crawl_err:
                print(f"Crawl4AI failed ({crawl_err}), falling back to native fetch...")
                resp = await client.get(url, timeout=30.0)
                resp.raise_for_status()
                html = resp.text
                from bs4 import BeautifulSoup
                import markdownify
                soup = BeautifulSoup(html, 'html.parser')
                markdown = markdownify.markdownify(str(soup), heading_style="ATX")
                
            doc_id = str(uuid.uuid4())
            version_hash = str(uuid.uuid4()) # simplified hash
            
            # store raw
            html_bytes = html.encode('utf-8')
            markdown_bytes = markdown.encode('utf-8')
            minio.put_object("raw", f"{doc_id}/v{version_hash}/page.html", io.BytesIO(html_bytes), len(html_bytes))
            minio.put_object("raw", f"{doc_id}/v{version_hash}/page.md", io.BytesIO(markdown_bytes), len(markdown_bytes))
            
            async with pool.acquire() as conn:
                existing = await conn.fetchrow("SELECT id FROM documents WHERE canonical_url = $1", url)
                if existing:
                    actual_doc_id = existing['id']
                else:
                    actual_doc_id = uuid.UUID(doc_id)
                    await conn.execute(
                        "INSERT INTO documents (id, source_id, canonical_url, status) VALUES ($1, $2, $3, 'PROCESSED')",
                        actual_doc_id, uuid.UUID(data["source_id"]), url
                    )
                
                await conn.execute(
                    "INSERT INTO document_versions (document_id, version_hash, s3_raw_uri) VALUES ($1, $2, $3)",
                    actual_doc_id, version_hash, f"s3://raw/{doc_id}/v{version_hash}/page.md"
                )
                await conn.execute(
                    "UPDATE discovered_urls SET is_processed = TRUE WHERE id = $1",
                    uuid.UUID(data["url_id"])
                )
            
            await process_queue.add("process", {"doc_id": str(actual_doc_id), "version_hash": version_hash})
    except Exception as e:
        error_msg = f"Crawl error for {url}: {e}"
        print(error_msg)
        async with pool.acquire() as conn:
            await conn.execute("UPDATE discovered_urls SET is_processed = TRUE, url = url || '#ERROR:' || $1 WHERE id = $2", error_msg, uuid.UUID(data["url_id"]))
