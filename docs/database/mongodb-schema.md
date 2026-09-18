# MongoDB Knowledge Schema

MongoDB is used exclusively for the RAG knowledge layer. It stores processed knowledge documents and their chunked, embedded representations to enable efficient vector search and metadata filtering.

## Collections

### 1. `knowledge_documents`
Stores document-level metadata and provenance.

```json
{
  "_id": "ObjectId",
  "document_id": "UUID (references PostgreSQL documents.id)",
  "version_hash": "string (references PostgreSQL document_versions.version_hash)",
  "canonical_url": "string",
  "title": "string",
  "source_name": "string",
  "source_type": "string",
  "companies": ["UUID"], 
  "roles": ["UUID"],
  "topics": ["UUID"],
  "publication_date": "ISODate",
  "crawl_date": "ISODate",
  "content_hash": "string (SHA-256 of processed markdown)",
  "relevance_score": "double",
  "quality_metadata": {
    "language": "string",
    "word_count": "int",
    "readability_score": "double"
  },
  "storage_uri": "string (S3 URI of processed markdown)",
  "provenance": {
    "crawl_job_id": "UUID",
    "discovered_url_id": "UUID"
  }
}
```

### 2. `knowledge_chunks`
Stores chunked text and vector embeddings for semantic search.

```json
{
  "_id": "ObjectId",
  "chunk_id": "UUID",
  "document_id": "UUID (references PostgreSQL documents.id)",
  "document_version": "string (references PostgreSQL document_versions.version_hash)",
  "chunk_index": "int",
  "text": "string (chunk content)",
  "section_path": "string (e.g., 'H1 > H2 > H3')",
  "embedding": ["double"], // Vector embedding array (e.g., 1536 dimensions for OpenAI Ada)
  "company_ids": ["UUID"],
  "role_ids": ["UUID"],
  "topic_ids": ["UUID"],
  "source_type": "string",
  "document_type": "string",
  "language": "string",
  "token_count": "int"
}
```
