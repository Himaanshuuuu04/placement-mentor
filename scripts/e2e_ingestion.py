import asyncio
import httpx
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Assuming running inside or with access to the environment
POSTGRES_DSN = os.environ.get('POSTGRES_DSN', 'postgres://ai_mentor:postgres@postgres:5432/ai_mentor_db')
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017')
API_URL = "http://localhost:8000/ingestion"

async def init_db():
    print("Applying postgres schema...")
    try:
        conn = await asyncpg.connect(POSTGRES_DSN)
        with open("/home/himanshu/projects/ai_mentor/docs/database/postgres-schema.sql", "r") as f:
            schema = f.read()
        await conn.execute(schema)
        await conn.close()
        print("Schema applied.")
    except Exception as e:
        print(f"Schema application error (might already exist): {e}")

async def run_test():
    await init_db()
    
    print("Creating source...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{API_URL}/sources", json={
                "name": "Google Careers",
                "base_url": "https://careers.google.com/",
                "source_type": "OFFICIAL_CAREERS"
            })
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

    print("Checking MongoDB for results...")
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client.ai_mentor
        docs = await db.knowledge_documents.count_documents({})
        chunks = await db.knowledge_chunks.count_documents({})
        print("==============================")
        print("INGESTION METRICS")
        print(f"Documents processed: {docs}")
        print(f"Chunks embedded: {chunks}")
        print("==============================")
        client.close()
    except Exception as e:
        print(f"Mongo error: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
