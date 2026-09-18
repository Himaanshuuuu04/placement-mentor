from bullmq import Queue
from shared.storage import get_minio
from shared.config import settings
import ollama
import json

dedup_queue = Queue("document-deduplicate", {"connection": {"host": settings.redis_host, "port": settings.redis_port}})

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
