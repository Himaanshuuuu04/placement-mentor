import asyncio
import httpx
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Assuming running inside or with access to the environment
POSTGRES_DSN = os.environ.get('POSTGRES_DSN', 'postgres://ai_mentor:postgres@postgres:5432/ai_mentor_db')
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017')
API_URL = os.environ.get('API_URL', 'http://knowledge-ingestion:8000/ingestion')

async def init_db():
    print(f"Applying postgres schema using DSN: {POSTGRES_DSN}")
    try:
        conn = await asyncpg.connect(POSTGRES_DSN)
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "database", "postgres-schema.sql"), "r") as f:
            schema = f.read()
        await conn.execute(schema)
        await conn.close()
        print("Schema applied.")
    except Exception as e:
        print(f"Schema application error (might already exist): {e}")

async def run_test():
    await init_db()
    
    print(f"Creating source using API_URL: {API_URL} ...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{API_URL}/sources", json={
                "name": "HTTPBin",
                "base_url": "https://httpbin.org/html",
                "source_type": "OFFICIAL_CAREERS"
            })
            print(resp)
            source_id = resp.json()["id"]
            print(f"Source ID: {source_id}")
            
            print("Creating job...")
            resp = await client.post(f"{API_URL}/jobs", json={
                "source_id": source_id
            })
            job_id = resp.json()["id"]
            print(f"Job ID: {job_id}")
    except Exception as e:
        print(f"API Error: {e}. Are services running?")
        return

    print("Waiting for ingestion pipeline (simulate 15 seconds)...")
    await asyncio.sleep(15)
    print("Waiting for ingestion pipeline (simulate 60 seconds)...")
    await asyncio.sleep(60)

    print("\n--- PIPELINE DIAGNOSTICS ---")
    try:
        conn = await asyncpg.connect(POSTGRES_DSN)
        jobs = await conn.fetch("SELECT * FROM crawl_jobs ORDER BY started_at DESC LIMIT 1")
        for j in jobs: print(f"Crawl Job: {j['id']} | Status: {j['status']}")
        
        urls = await conn.fetch("SELECT * FROM discovered_urls ORDER BY discovered_at DESC")
        print(f"Discovered URLs count: {len(urls)}")
        for u in urls[:5]: print(f"  -> {u['url']} (Processed: {u['is_processed']})")
        
        docs_pg = await conn.fetch("SELECT * FROM documents")
        print(f"Documents in Postgres: {len(docs_pg)}")
        for d in docs_pg[:5]: print(f"  -> {d['canonical_url']} | Status: {d['status']}")
        await conn.close()
    except Exception as e:
        print(f"Postgres debug error: {e}")

    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client.ai_mentor
        docs = await db.knowledge_documents.count_documents({})
        chunks = await db.knowledge_chunks.count_documents({})
        print(f"Documents in Mongo: {docs}")
        print(f"Chunks in Mongo: {chunks}")
        
        if docs > 0:
            doc = await db.knowledge_documents.find_one({})
            print(f"Sample Mongo Doc metadata keys: {list(doc.get('metadata', {}).keys())}")
        
        client.close()
    except Exception as e:
        print(f"Mongo debug error: {e}")
    print("----------------------------\n")

if __name__ == "__main__":
    asyncio.run(run_test())
