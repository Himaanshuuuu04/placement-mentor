import os
import sys
import asyncio
import urllib.request
import psycopg2
from pymongo import MongoClient
import redis
from bullmq import Queue

services = [
    "api-gateway", "identity", "company", "question", "assessment", 
    "evaluation", "mastery", "interview", "roadmap", "agent-orchestrator", 
    "retrieval", "discovery", "crawler", "document-processor", "classifier", 
    "deduplication", "embedding", "code-execution", "realtime", "knowledge-ingestion"
]

def verify_health_endpoints():
    print("--- Verifying Service Health Endpoints ---")
    port = 8001
    all_good = True
    for svc in services:
        url = f"http://localhost:{port}/health"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.status == 200:
                    print(f"[OK] {svc} (Port {port})")
                else:
                    print(f"[FAIL] {svc} returned {response.status}")
                    all_good = False
        except Exception as e:
            print(f"[FAIL] {svc} (Port {port}): {e}")
            all_good = False
        port += 1
    return all_good

def verify_postgres():
    print("\n--- Verifying PostgreSQL Connectivity ---")
    dsn = os.getenv("POSTGRES_DSN", "postgresql://ai_mentor:postgres@localhost:5432/ai_mentor_db")
    try:
        conn = psycopg2.connect(dsn)
        conn.close()
        print("[OK] PostgreSQL connected")
        return True
    except Exception as e:
        print(f"[FAIL] PostgreSQL connection failed: {e}")
        return False

def verify_redis_and_bullmq():
    print("\n--- Verifying Redis Connectivity & BullMQ ---")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    
    try:
        r = redis.Redis(host=redis_host, port=redis_port)
        r.ping()
        print("[OK] Redis connected")
    except Exception as e:
        print(f"[FAIL] Redis connection failed: {e}")
        return False

    # Publish test BullMQ event
    async def publish_event():
        try:
            queue = Queue("test-queue", {"connection": {"host": redis_host, "port": redis_port}})
            await queue.add("test-job", {"msg": "Hello BullMQ"})
            print("[OK] BullMQ test event published")
            return True
        except Exception as e:
            print(f"[FAIL] BullMQ publishing failed: {e}")
            return False
            
    return asyncio.run(publish_event())

def verify_localstack():
    print("\n--- Verifying LocalStack Connectivity ---")
    try:
        req = urllib.request.Request("http://localhost:4566/_localstack/health")
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                print("[OK] LocalStack connected")
                return True
            else:
                print(f"[FAIL] LocalStack returned {response.status}")
                return False
    except Exception as e:
        print(f"[FAIL] LocalStack connection failed: {e}")
        return False

def verify_crawl4ai():
    print("\n--- Verifying Crawl4AI Connectivity ---")
    try:
        # Just check if port 11225 is responding
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(("localhost", 11225))
        s.close()
        print("[OK] Crawl4AI connected")
        return True
    except Exception as e:
        print(f"[FAIL] Crawl4AI connection failed: {e}")
        return False

def verify_mongo():
    print("\n--- Verifying MongoDB Atlas Connectivity ---")
    uri = os.getenv("MONGO_URI", "mongodb://admin:admin@localhost:27017/")
    if "cluster.mongodb.net" in uri and "user:pass" in uri:
        print("[SKIP] Default template URI detected. Please configure actual Atlas URI.")
        return True
        
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("[OK] MongoDB connected")
        return True
    except Exception as e:
        print(f"[FAIL] MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    h = verify_health_endpoints()
    p = verify_postgres()
    r = verify_redis_and_bullmq()
    m = verify_localstack()
    c = verify_crawl4ai()
    mo = verify_mongo()
    
    if all([h, p, r, m, c, mo]):
        print("\nAll verifications passed successfully!")
        sys.exit(0)
    else:
        print("\nSome verifications failed.")
        sys.exit(1)
