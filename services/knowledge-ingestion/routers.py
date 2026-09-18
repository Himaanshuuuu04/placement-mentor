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
