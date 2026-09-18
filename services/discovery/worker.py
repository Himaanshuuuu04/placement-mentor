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
