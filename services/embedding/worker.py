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
    chunks = [c for c in markdown.split('\n\n') if len(c.strip()) > 50]
    
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
