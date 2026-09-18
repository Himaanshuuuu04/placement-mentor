import asyncio
import os
import sys
import uuid

# Add services and packages to Python path
sys.path.append("/app")
sys.path.append("/app/packages/shared")
sys.path.append("/app/services/discovery")
sys.path.append("/app/services/crawler")
sys.path.append("/app/services/document-processor")

from shared.db import init_postgres, get_postgres
from shared.storage import init_minio, get_minio

# Import worker functions
from services.discovery.worker import process_discovery
from services.crawler.worker import process_fetch

class MockJob:
    def __init__(self, data):
        self.data = data

async def run_pipeline():
    print("\n--- Initializing Infrastructure Connections ---")
    await init_postgres()
    init_minio()
    print("Database and MinIO connected.")

    # 1. Setup Mock Job Data
    job_id = str(uuid.uuid4())
    source_id = str(uuid.uuid4())
    
    pool = get_postgres()
    async with pool.acquire() as conn:
        # Create a mock source
        await conn.execute(
            "INSERT INTO knowledge_sources (id, name, base_url, source_type) VALUES ($1, $2, $3, $4)",
            uuid.UUID(source_id), "Test Source", "https://example.com", "OFFICIAL_CAREERS"
        )
        # Create a mock crawl job
        await conn.execute(
            "INSERT INTO crawl_jobs (id, source_id, status) VALUES ($1, $2, 'PENDING')",
            uuid.UUID(job_id), uuid.UUID(source_id)
        )
    print(f"\n--- Testing DISCOVERY Microservice ---")
    discovery_job = MockJob({"job_id": job_id, "source_id": source_id})
    try:
        await process_discovery(discovery_job, None)
        print("Discovery worker executed successfully.")
    except Exception as e:
        print(f"Discovery worker failed: {e}")
        return

    # Check what discovery inserted
    async with pool.acquire() as conn:
        urls = await conn.fetch("SELECT id, url FROM discovered_urls WHERE crawl_job_id = $1", uuid.UUID(job_id))
        print(f"Discovery found {len(urls)} URLs: {[u['url'] for u in urls]}")
        if not urls:
            return
        
        url_id = str(urls[0]['id'])
        target_url = urls[0]['url']

    print(f"\n--- Testing CRAWLER Microservice ---")
    print(f"Crawling {target_url}...")
    fetch_job = MockJob({"url_id": url_id, "url": target_url, "source_id": source_id})
    try:
        await process_fetch(fetch_job, None)
        print("Crawler worker executed successfully.")
    except Exception as e:
        print(f"Crawler worker failed: {e}")
        return

    # Check what crawler inserted
    async with pool.acquire() as conn:
        url_record = await conn.fetchrow("SELECT url, is_processed FROM discovered_urls WHERE id = $1", uuid.UUID(url_id))
        print(f"URL Status after crawl: {url_record['url']} (Processed: {url_record['is_processed']})")
        
        docs = await conn.fetch("SELECT id, status FROM documents WHERE source_id = $1", uuid.UUID(source_id))
        print(f"Crawler inserted {len(docs)} documents.")
        if not docs:
            return
            
        doc_id = str(docs[0]['id'])
        
        versions = await conn.fetch("SELECT version_hash FROM document_versions WHERE document_id = $1", uuid.UUID(doc_id))
        version_hash = versions[0]['version_hash']

    print(f"\n--- Testing DOCUMENT-PROCESSOR Microservice ---")
    doc_job = MockJob({"doc_id": doc_id, "version_hash": version_hash})
    try:
        # Import dynamically because it has hyphens in the path
        import importlib.util
        spec = importlib.util.spec_from_file_location("doc_worker", "/app/services/document-processor/worker.py")
        doc_worker = importlib.util.module_from_spec(spec)
        sys.modules["doc_worker"] = doc_worker
        spec.loader.exec_module(doc_worker)
        
        await doc_worker.process_document(doc_job, None)
        print("Document Processor worker executed successfully.")
    except Exception as e:
        print(f"Document Processor worker failed: {e}")
        return

    print("\nAll tested microservices successfully executed their logic locally!")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
