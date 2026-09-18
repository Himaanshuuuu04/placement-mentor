# 04. Data Architecture

## 1. Storage Categories
Data is explicitly partitioned across four specialized storage systems to align with read/write patterns, structure, and access requirements.

1. **PostgreSQL**: System of record for highly structured, transactional application state.
2. **MongoDB**: Vector database and metadata store for the RAG knowledge layer.
3. **S3 (Object Storage)**: Blob storage for raw crawled artifacts (HTML/Markdown) and execution outputs.
4. **Redis**: Ephemeral state, distributed locks, and message queues (BullMQ).

## 2. Data Ownership Matrix
*Important Rule: No service may access another service's database schema/tables directly. All access must traverse defined APIs or events.*

| Entity | Owning Service | Storage | Access Method | Source of Truth |
|---|---|---|---|---|
| User, UserProfile | Identity Service | PostgreSQL | API / Event | PostgreSQL |
| Company, Role, Competency | Company & Role Service | PostgreSQL | API | PostgreSQL |
| Topic, Question, Q-Topics | Question Bank Service| PostgreSQL | API | PostgreSQL |
| Assessment, Submission | Assessment Service | PostgreSQL | API | PostgreSQL |
| ExecutionJob, Result | Code Execution Service | PostgreSQL | API / Event | PostgreSQL |
| Evaluation | Evaluation Service | PostgreSQL | API / Event | PostgreSQL |
| StudentMastery, MasteryEvent| Mastery Service | PostgreSQL | API / Event | PostgreSQL |
| InterviewSession, Turn | Interview Service | PostgreSQL | API / Event | PostgreSQL |
| Roadmap, RoadmapItem | Roadmap Service | PostgreSQL | API / Event | PostgreSQL |
| CrawlJob, DiscoveredURL | Crawl Service | PostgreSQL | Queue | PostgreSQL |
| Raw Document Artifacts | Crawl Service | S3 | S3 API | S3 |
| Document, Chunk, Embedding| Indexing Service | MongoDB | API | MongoDB |
| AgentSession, Checkpoint | Agent Orchestrator | PostgreSQL | PostgresSaver | PostgreSQL |

## 3. PostgreSQL Database Architecture
PostgreSQL stores highly normalized relational schemas. 

**Design Guidelines:**
- **Foreign Keys**: Enforce strict foreign keys *only within* a service's bounded context. Avoid cross-service foreign keys; use soft references (e.g., UUID columns) instead.
- **Constraints**: Heavily leverage `CHECK` constraints, `UNIQUE` constraints, and robust data typing.
- **Partitioning**: Only applied to high-volume, append-only event tables (e.g., `mastery_events`, `interview_turns`) based on time-series analysis to ensure performance during data growth. Do not introduce partitioning preemptively.

## 4. MongoDB Knowledge Schema
MongoDB handles the unstructured and semi-structured requirements of the RAG platform.

**Collection: `knowledge_documents`**
- *Attributes*: document ID, version, canonical URL, title, source type, company, role, topics, publication date, crawl date, content hash, relevance information, storage URI.
- *Indexes*: Indexed for rapid metadata filtering (Company, Role, Topic) and text-based lookup.

**Collection: `knowledge_chunks`**
- *Attributes*: chunk ID, document ID, document version, chunk index, text, section path, embedding (vector), company IDs, role IDs, topic IDs, token count.
- *Indexes*: Vector Search index on the `embedding` field. Compound indexes on metadata (`company_ids`, `topic_ids`) for efficient pre-filtering prior to vector similarity search.

## 5. Raw Document Storage (S3)
Maintains absolute data provenance. Provides a mechanism to re-process and re-embed documents if parsing or embedding models change, without needing to re-crawl the live web.

**Naming Conventions:**
- `s3://knowledge-bucket/raw/{source_domain}/{document_id}/v{version}/page.html`
- `s3://knowledge-bucket/processed/{source_domain}/{document_id}/v{version}/content.md`

## 6. Redis Architecture
Redis is explicitly **NOT** used as a system of record.
- **BullMQ Queues**: Drives the asynchronous, event-driven processes: `crawl-discovery`, `crawl-fetch`, `document-process`, `document-classify`, `document-deduplicate`, `document-embed`, `evaluation`, `mastery-update`, `question-generation`.
- **Idempotency & Concurrency**: Manages distributed locks and rate limits to control worker concurrency and ensure idempotency during failures.
