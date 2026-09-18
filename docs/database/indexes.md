# Indexing Strategy

This document outlines the indexing strategy for both PostgreSQL (System of Record) and MongoDB (RAG/Vector Search) stores.

## PostgreSQL Indexing

### Primary Keys & Foreign Keys
- **Primary Keys:** Every table uses a `UUID` primary key, automatically indexed.
- **Foreign Keys:** Indexes are applied to all frequently queried foreign keys, such as `user_id`, `company_id`, `topic_id`, and `session_id`.

### High-Cardinality & Query Pattern Indexes
- **Users:** `CREATE INDEX idx_users_email ON users(email);` for fast authentication lookup.
- **Questions:** `CREATE INDEX idx_questions_difficulty ON questions(difficulty);` to rapidly filter questions by difficulty during adaptive generation.
- **Submissions:** `CREATE INDEX idx_submissions_user_id ON submissions(user_id);` to load student history.
- **Mastery Events:** `CREATE INDEX idx_mastery_events_user_topic ON mastery_events(user_id, topic_id);` for time-series aggregation of mastery state.
- **Interviews:** `CREATE INDEX idx_interview_turns_session ON interview_turns(session_id, turn_sequence);` to rapidly assemble interview history for LLM context.
- **Ingestion:** `CREATE INDEX idx_documents_url ON documents(canonical_url);` to prevent duplicate crawls and support deduplication.

### Partitioning Strategy
- **`mastery_events`**: Candidate for range partitioning by `created_at` (e.g., monthly) if the event volume grows significantly.
- **`interview_turns`**: Candidate for range partitioning by `created_at` or hash partitioning by `session_id`.

## MongoDB Indexing

MongoDB indexing is specifically optimized for RAG (Retrieval-Augmented Generation) workloads.

### 1. Vector Search
- **Index Type:** Atlas Vector Search Index (HNSW)
- **Field:** `knowledge_chunks.embedding`
- **Purpose:** Fast approximate nearest neighbor (ANN) search for semantic retrieval.

### 2. Metadata Filtering
- **Index Type:** Compound Index
- **Fields:** `{ company_ids: 1, role_ids: 1, topic_ids: 1 }`
- **Purpose:** Pre-filtering vectors based on the student's target company, role, or active topic before performing ANN search.

### 3. Full-Text Search
- **Index Type:** Text Index
- **Field:** `knowledge_chunks.text`, `knowledge_documents.title`
- **Purpose:** Keyword-based retrieval to complement semantic search in a hybrid retrieval approach.

### 4. Document Lookup & Deduplication
- **Index Type:** Unique Index
- **Field:** `knowledge_documents.canonical_url`
- **Purpose:** URL-level canonical deduplication (Level 1).
- **Index Type:** Unique Index
- **Field:** `knowledge_documents.content_hash`
- **Purpose:** Exact content hashing deduplication (Level 2).
- **Index Type:** Standard Index
- **Field:** `knowledge_chunks.document_id`
- **Purpose:** Fetching all chunks belonging to a specific document.
