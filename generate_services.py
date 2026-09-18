import os

services = {
    'knowledge-ingestion': {
        'main.py': '''
import logging
from fastapi import Request
from shared.api import create_app
from shared.config import settings
from .routers import router

app = create_app("knowledge-ingestion")
app.include_router(router, prefix="/ingestion")
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting knowledge-ingestion service.")
''',
        'routers.py': '''
import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from bullmq import Queue
from shared.config import settings
import asyncpg
from shared.db import get_postgres, init_postgres

router = APIRouter()
crawl_queue = Queue("crawl-discovery", {"connection": {"host": settings.redis_host, "port": settings.redis_port}})

class SourceCreate(BaseModel):
    name: str
    base_url: str
    source_type: str

class JobCreate(BaseModel):
    source_id: str

@router.on_event("startup")
async def startup():
    await init_postgres()

@router.post("/sources")
async def create_source(source: SourceCreate):
    pool = get_postgres()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO knowledge_sources (name, base_url, source_type) VALUES ($1, $2, $3) RETURNING id",
            source.name, source.base_url, source.source_type
        )
    return {"id": str(row["id"])}

@router.get("/sources")
async def get_sources():
    pool = get_postgres()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, base_url, source_type FROM knowledge_sources")
    return [{"id": str(r["id"]), "name": r["name"], "base_url": r["base_url"], "source_type": r["source_type"]} for r in rows]

@router.post("/jobs")
async def create_job(job: JobCreate):
    pool = get_postgres()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO crawl_jobs (source_id, status) VALUES ($1, 'PENDING') RETURNING id",
            uuid.UUID(job.source_id)
        )
    job_id = str(row["id"])
    await crawl_queue.add("discover", {"job_id": job_id, "source_id": job.source_id})
    return {"id": job_id}

@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    pool = get_postgres()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id, status, started_at, completed_at FROM crawl_jobs WHERE id = $1", uuid.UUID(job_id))
    if not row:
        return {"error": "not found"}
    return dict(row)
'''
    },
    'discovery': {
        'main.py': '''
import asyncio
from bullmq import Worker
from shared.config import settings
from .worker import process_discovery

async def main():
    worker = Worker("crawl-discovery", process_discovery, {"connection": {"host": settings.redis_host, "port": settings.redis_port}})
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
''',
        'worker.py': '''
from bullmq import Queue
from shared.db import get_postgres, init_postgres
import uuid
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

crawl_fetch_queue = Queue("crawl-fetch", {"connection": {"host": "redis", "port": 6379}})

async def process_discovery(job, job_token):
    await init_postgres()
    pool = get_postgres()
    data = job.data
    job_id = data["job_id"]
    source_id = data["source_id"]
    
    async with pool.acquire() as conn:
        source = await conn.fetchrow("SELECT base_url FROM knowledge_sources WHERE id = $1", uuid.UUID(source_id))
        await conn.execute("UPDATE crawl_jobs SET status = 'CRAWLING', started_at = NOW() WHERE id = $1", uuid.UUID(job_id))
        
    base_url = source["base_url"]
    
    # Very simple seed discovery for E2E test
    urls_to_crawl = [base_url]
    
    # Attempt to fetch the base URL to find more links (depth 1)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(base_url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                full_url = urljoin(base_url, a['href'])
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    urls_to_crawl.append(full_url)
    except Exception as e:
        print(f"Error extracting links: {e}")
        
    urls_to_crawl = list(set(urls_to_crawl))[:100] # Limit to 100 for E2E test
    
    async with pool.acquire() as conn:
        for url in urls_to_crawl:
            # canonicalize by removing fragments
            canonical_url = url.split('#')[0]
            try:
                row = await conn.fetchrow(
                    "INSERT INTO discovered_urls (crawl_job_id, url) VALUES ($1, $2) RETURNING id",
                    uuid.UUID(job_id), canonical_url
                )
                await crawl_fetch_queue.add("fetch", {"url_id": str(row["id"]), "url": canonical_url, "source_id": source_id})
            except asyncpg.exceptions.UniqueViolationError:
                pass
'''
    },
    'crawler': {
        'main.py': '''
import asyncio
from bullmq import Worker
from shared.config import settings
from .worker import process_fetch

async def main():
    worker = Worker("crawl-fetch", process_fetch, {"connection": {"host": settings.redis_host, "port": settings.redis_port}})
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
''',
        'worker.py': '''
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
'''
    },
    'document-processor': {
        'main.py': '''
import asyncio
from bullmq import Worker
from shared.config import settings
from .worker import process_document

async def main():
    worker = Worker("document-process", process_document, {"connection": {"host": settings.redis_host, "port": settings.redis_port}})
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
''',
        'worker.py': '''
from bullmq import Queue
from shared.storage import get_minio
from shared.db import get_postgres, init_postgres
import io
import uuid

classify_queue = Queue("document-classify", {"connection": {"host": "redis", "port": 6379}})

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
    
    minio.put_object("processed", f"{doc_id}/v{version}/clean.md", io.BytesIO(processed.encode()), len(processed))
    
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE document_versions SET s3_processed_uri = $1 WHERE document_id = $2 AND version_hash = $3",
            f"s3://processed/{doc_id}/v{version}/clean.md", uuid.UUID(doc_id), version
        )
        
    await classify_queue.add("classify", {"doc_id": doc_id, "version_hash": version})
'''
    },
    'classifier': {
        'main.py': '''
import asyncio
from bullmq import Worker
from shared.config import settings
from .worker import process_classify

async def main():
    worker = Worker("document-classify", process_classify, {"connection": {"host": settings.redis_host, "port": settings.redis_port}})
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
''',
        'worker.py': '''
from bullmq import Queue
from shared.storage import get_minio
from shared.config import settings
import ollama
import json

dedup_queue = Queue("document-deduplicate", {"connection": {"host": "redis", "port": 6379}})

async def process_classify(job, job_token):
    minio = get_minio()
    data = job.data
    doc_id = data["doc_id"]
    version = data["version_hash"]
    
    obj = minio.get_object("processed", f"{doc_id}/v{version}/clean.md")
    markdown = obj.read().decode('utf-8')
    
    # Use ollama to classify
    client = ollama.AsyncClient(host=settings.ollama_base_url)
    try:
        # Prompt for structured JSON
        prompt = f"""
        Analyze this text and output JSON with these keys: relevant (bool), document_type (string), companies (list of string), roles (list of string), topics (list of string).
        Text: {markdown[:1000]}
        """
        response = await client.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}], format='json')
        classification = json.loads(response['message']['content'])
        
        if classification.get('relevant', True):
            await dedup_queue.add("dedup", {"doc_id": doc_id, "version_hash": version, "metadata": classification})
    except Exception as e:
        print(f"Classification error: {e}")
'''
    },
    'deduplication': {
        'main.py': '''
import asyncio
from bullmq import Worker
from shared.config import settings
from .worker import process_dedup

async def main():
    worker = Worker("document-deduplicate", process_dedup, {"connection": {"host": settings.redis_host, "port": settings.redis_port}})
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
''',
        'worker.py': '''
from bullmq import Queue
import hashlib

embed_queue = Queue("document-embed", {"connection": {"host": "redis", "port": 6379}})

async def process_dedup(job, job_token):
    # Level 1 (URL) is handled in DB
    # Level 2 (Hash) implementation logic:
    # Here we simulate checking if content is duplicated.
    data = job.data
    await embed_queue.add("embed", data)
'''
    },
    'embedding': {
        'main.py': '''
import asyncio
from bullmq import Worker
from shared.config import settings
from .worker import process_embed

async def main():
    worker = Worker("document-embed", process_embed, {"connection": {"host": settings.redis_host, "port": settings.redis_port}})
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
''',
        'worker.py': '''
from shared.storage import get_minio
from shared.db import get_mongo, init_mongo, get_postgres, init_postgres
import ollama
from shared.config import settings
import uuid

async def process_embed(job, job_token):
    await init_mongo()
    await init_postgres()
    mongo = get_mongo()
    db = mongo.ai_mentor
    
    minio = get_minio()
    data = job.data
    doc_id = data["doc_id"]
    version = data["version_hash"]
    metadata = data["metadata"]
    
    obj = minio.get_object("processed", f"{doc_id}/v{version}/clean.md")
    markdown = obj.read().decode('utf-8')
    
    # Structural chunking (naive for E2E)
    chunks = [c for c in markdown.split('\\n\\n') if len(c.strip()) > 50]
    
    client = ollama.AsyncClient(host=settings.ollama_base_url)
    
    # Store doc
    await db.knowledge_documents.insert_one({
        "document_id": doc_id,
        "version": version,
        "metadata": metadata
    })
    
    for i, chunk in enumerate(chunks):
        try:
            embed_resp = await client.embeddings(model='nomic-embed-text', prompt=chunk)
            embedding = embed_resp['embedding']
            await db.knowledge_chunks.insert_one({
                "chunk_id": str(uuid.uuid4()),
                "document_id": doc_id,
                "chunk_index": i,
                "text": chunk,
                "embedding": embedding,
                "metadata": metadata
            })
        except Exception as e:
            print(f"Embedding error: {e}")
'''
    }
}

for service, files in services.items():
    base_dir = f"/home/himanshu/projects/ai_mentor/services/{service}"
    os.makedirs(base_dir, exist_ok=True)
    for file, content in files.items():
        with open(os.path.join(base_dir, file), "w") as f:
            f.write(content.strip() + "\n")
print("Services generated successfully.")
