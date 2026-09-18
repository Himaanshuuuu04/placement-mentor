import asyncio
import asyncpg

async def check():
    conn = await asyncpg.connect("postgresql://ai_mentor:postgres@127.0.0.1:5432/ai_mentor_db")
    
    print("Crawl Jobs:")
    rows = await conn.fetch("SELECT * FROM crawl_jobs")
    for r in rows:
        print(dict(r))
        
    print("\nDiscovered URLs:")
    rows = await conn.fetch("SELECT id, crawl_job_id, url, is_processed FROM discovered_urls")
    for r in rows:
        print(dict(r))
        
    print("\nDocuments:")
    rows = await conn.fetch("SELECT id, status, canonical_url FROM documents")
    for r in rows:
        print(dict(r))
        
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check())
