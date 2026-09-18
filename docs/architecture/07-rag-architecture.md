# 07. RAG Architecture

## 1. Overview
The Retrieval-Augmented Generation (RAG) architecture provides critical contextual knowledge to the AI Agents (such as the Interview Conductor and System Design Mentor). It grounds LLM reasoning in verified company-specific data, recent interview experiences, and accurate technical documentation.

## 2. The Retrieval Pipeline
The system executes retrieval through a multi-stage pipeline designed to maximize precision and mitigate hallucination.

**Pipeline Flow:**
`User Query / Agent Tool Call`
↓
**Query Normalization**: Cleans the input text and resolves coreferences based on current conversational state.
↓
**Intent & Topic Extraction**: Identifies target companies, roles, and technical topics using lightweight classification or deterministic keyword matching.
↓
**Metadata Pre-Filtering**: Narrows the MongoDB Vector Search space using the extracted tags (e.g., `company_id == "google"`). This significantly reduces latency and ensures relevance.
↓
**Hybrid Retrieval**:
  - *Vector Search*: Uses dense embeddings to find semantic similarity.
  - *Keyword Search (BM25)*: Uses exact match for technical jargon, acronyms, and specific API identifiers.
↓
**Hybrid Ranking**: Merges vector and keyword results utilizing algorithms like Reciprocal Rank Fusion (RRF).
↓
**Reranking**: Applies a Cross-Encoder model to score the top-K retrieved documents directly against the query, yielding absolute relevance scores.
↓
**Context Assembly**: Formats the highest-scoring chunks while strictly respecting the LLM context window limits.
↓
**LLM Generation**: Provides assembled, cited context to the Agent for final reasoning.

## 3. Embedding & Chunking Strategy
- **Embedding Model**: Abstracted behind an interface to allow swapping. Configured for a high-performing model (e.g., OpenAI `text-embedding-3-large` or Cohere) with tunable vector dimensions.
- **Chunking Strategy**: Employs Markdown-aware semantic chunking.
  - **Size Target**: ~512-1024 tokens per chunk.
  - **Overlap**: ~10-15% (50-150 tokens) to prevent context loss at chunk boundaries.
  - **Structure**: Respects markdown header hierarchies (`##`, `###`) to ensure cohesive thoughts are not split arbitrarily.

## 4. Provenance & Traceability
The architecture enforces strict data provenance tracking from ingestion to final output. This ensures transparency and allows the system to trace hallucinations back to their source.
1. **Source**: Canonical URL tracked in S3.
2. **Document**: Uniquely identified document version in the database.
3. **Chunk**: Every vector chunk contains `document_id` and `version` metadata.
4. **Retrieval Result**: Search returns chunks alongside full citation metadata.
5. **Generation**: Agents are explicitly prompted to cite sources (e.g., "[1]") when providing factual or company-specific data.

## 5. RAG Security & Data Isolation
- **Status of Data**: RAG data is considered *trusted* technically (it won't execute malicious code), but *probabilistic* factually (it may contain errors).
- **Poisoning Mitigation**: Relevance Classifiers in the Knowledge Ingestion Pipeline aggressively drop malicious, irrelevant, or spam payloads before they ever reach the embedding phase.
- **System Prompt Safeguards**: Agents are instructed to prioritize fundamental computer science principles over retrieved context if the retrieved text appears contradictory or factually corrupted.
