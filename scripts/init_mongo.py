import os
from pymongo import MongoClient
import re

def init_mongo():
    uri = os.getenv("MONGO_URI", "mongodb://admin:admin@localhost:27017/")
    if not uri or uri == "":
        print("MONGO_URI not set. Skipping MongoDB initialization.")
        return
        
    print(f"Connecting to MongoDB at {uri}...")
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Verify connection
        client.admin.command('ping')
        
        db = client.get_database("ai_mentor")
        print("Connected. Creating indexes based on docs/database/mongodb-schema.md...")
        
        # Creating collections and basic indexes
        docs = db.knowledge_documents
        docs.create_index("canonical_url", unique=True)
        docs.create_index("company")
        docs.create_index("role")
        docs.create_index("topics")
        
        chunks = db.knowledge_chunks
        chunks.create_index("document_id")
        
        print("MongoDB initialization successful.")
    except Exception as e:
        print(f"MongoDB initialization failed: {e}")
        exit(1)

if __name__ == "__main__":
    init_mongo()
