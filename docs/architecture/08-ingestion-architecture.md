# Web Ingestion Architecture

## 1. Overview
The Web Ingestion Architecture (PLANE C) is responsible for discovering, fetching, parsing, and processing knowledge documents (such as company interview experiences, algorithmic tutorials, and system design guides) from the web. The final output is chunked and embedded knowledge stored in MongoDB, with raw and processed artifacts retained in S3.

## 2. Ingestion Pipeline
The ingestion pipeline is decoupled from the crawler tool (Crawl4AI) to allow independent scaling, resilience, and complex processing logic. 

**Pipeline Flow:**
Source → Discovery Service → URL Normalization → URL Queue → Crawler Service (Crawl4AI) → Raw HTML/Markdown → Document Normalization → Relevance Classification → Metadata Extraction → Deduplication → Chunking → Embedding → MongoDB (Vector Index)

## 3. Component Responsibilities

### 3.1 Discovery Service
- **Role:** Finds new URLs to crawl based on seed domains, search queries, or sitemaps.
- **Features:** 
  - Parses `sitemap.xml`
  - Runs scheduled discovery tasks
  - Respects `robots.txt` policies
  - Applies domain restrictions to prevent infinite out-of-bounds crawling

### 3.2 Crawler Service
- **Role:** Fetches web content safely and efficiently using Crawl4AI.
- **Features:**
  - Manages crawl rate limits, retry logic, and exponential backoff.
  - Prevents resource exhaustion (e.g., rejecting huge pages).
  - Handles malicious redirects and prevents Server-Side Request Forgery (SSRF).
  - Drops unexpected file downloads (e.g., binaries, PDFs).
- **Queues (Redis/BullMQ):** Consumes from `crawl-fetch`.

### 3.3 Document Processor (Normalization)
- **Role:** Cleans raw HTML into structural markdown.
- **Flow:**
  - HTML → Main-content extraction (removing boilerplate/nav bars).
  - Boilerplate-free HTML → Markdown conversion.
- **Queues:** Consumes from `document-process`.

### 3.4 Classifier & Metadata Extractor
- **Role:** Evaluates document quality and extracts structured metadata.
- **Extracted Taxonomy:**
  - `source_type`, `document_type`, `company`, `role`, `topic`, `difficulty`, `language`, `published_at`, `author`, `confidence`, `relevance_score`
- **Relevance Threshold:** Documents that fail to meet a predefined relevance score are discarded and not embedded.
- **Queues:** Consumes from `document-classify`.

### 3.5 Deduplication Service
- **Role:** Ensures identical or semantically duplicate content is not re-indexed while preserving source provenance.
- **Three Levels of Deduplication:**
  1. **Level 1 (URL Canonicalization):** Strips tracking parameters, normalizes trailing slashes.
  2. **Level 2 (Exact Content Hashing):** Hashes the normalized markdown. If a hash match exists, skips processing but updates the provenance graph (e.g., appending the new URL as an alternative source).
  3. **Level 3 (Near-Duplicate Semantic Detection):** Uses similarity thresholds on text embeddings or MinHash to detect slightly modified clones.
- **Queues:** Consumes from `document-deduplicate`.

### 3.6 Chunking & Embedding Service
- **Role:** Breaks normalized documents into optimal context windows and generates vector embeddings.
- **Strategy:** 
  - Sentence or paragraph-aware chunking with token overlap.
  - Preserves hierarchical metadata (section paths, document IDs).
- **Queues:** Consumes from `document-chunk` and `document-embed`.

## 4. Raw Document Storage (S3)
Raw artifacts are persisted in S3 for auditing, reprocessing, and versioning.
- **Bucket Structure:**
  - `s3://knowledge-bucket/raw/{document_id}/v{version}/page.html`
  - `s3://knowledge-bucket/processed/{document_id}/v{version}/content.md`
- **Lifecycle Policies:** Keep raw HTML for 30 days, transition to Glacier; processed markdown kept indefinitely.
