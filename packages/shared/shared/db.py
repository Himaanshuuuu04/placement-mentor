import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from shared.config import settings

postgres_pool = None
mongo_client = None

async def init_postgres():
    global postgres_pool
    if settings.postgres_dsn and not postgres_pool:
        postgres_pool = await asyncpg.create_pool(dsn=settings.postgres_dsn)

async def init_mongo():
    global mongo_client
    if settings.mongo_uri and not mongo_client:
        mongo_client = AsyncIOMotorClient(settings.mongo_uri)

async def close_postgres():
    global postgres_pool
    if postgres_pool:
        await postgres_pool.close()

async def close_mongo():
    global mongo_client
    if mongo_client:
        mongo_client.close()

def get_postgres():
    if not postgres_pool:
        raise Exception("Postgres pool not initialized")
    return postgres_pool

def get_mongo():
    if not mongo_client:
        raise Exception("Mongo client not initialized")
    return mongo_client
