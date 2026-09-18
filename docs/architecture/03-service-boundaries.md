# 03. Service Boundaries

## 1. Architectural Style
The system adopts a modular microservices architecture defined by strict bounded contexts. Services are explicitly scoped by business responsibility, data ownership, and independently scalable workloads. 

**Core Rules:**
- **Encapsulation**: No service directly modifies another service's database tables.
- **Communication**: Cross-service communication must occur via explicit APIs (synchronous) or asynchronous Events (Redis/BullMQ).
- **Simplicity**: Avoid distributed system complexity unless it resolves a concrete scalability or decoupling problem.

## 2. Defined Service Boundaries

### Domain: API & Connectivity
1. **API Gateway / BFF**: 
   - *Responsibility*: Routing, authentication validation, and rate limiting.
2. **Realtime Gateway**: 
   - *Responsibility*: Manages stateful connections (WebSockets for chat/events, WebRTC signaling for audio).

### Domain: Identity & Configuration
3. **Identity / User Service**: 
   - *Responsibility*: Manages users, authentication mapping, and core user profiles.
4. **Company & Role Service**: 
   - *Responsibility*: Manages company profiles, target roles, and required competencies.
5. **Topic / Competency Service**: 
   - *Responsibility*: Owns the global taxonomy of technical concepts.

### Domain: Assessment & Learning
6. **Question Bank Service**: 
   - *Responsibility*: Manages questions, variants, test cases, and difficulty tagging.
7. **Assessment Service**: 
   - *Responsibility*: Orchestrates test sessions, tracks time limits, and collects code submissions.
8. **Code Execution Service**: 
   - *Responsibility*: Proxies requests to Judge0/Firecracker, managing limits, lifecycles, and security boundaries.
9. **Evaluation Service**: 
   - *Responsibility*: Analyzes execution results and static code attributes (often invokes AI agent tools).
10. **Knowledge Tracing / Mastery Service**: 
    - *Responsibility*: The system of record for student multidimensional mastery (LKT/IRT models).
11. **Roadmap / Personalization Service**: 
    - *Responsibility*: Generates structured, deterministic study plans based on mastery and target dates.

### Domain: AI & Interviews
12. **Agent Orchestrator**: 
    - *Responsibility*: Runs the LangGraph engine. Hosts the Router, Code Evaluator, Interview Conductor, and System Design Mentor. Exposes tools to agents.
13. **Interview Service**: 
    - *Responsibility*: Manages interview session lifecycle, conversation turns, and history. Ties into the Agent Orchestrator.
14. **Retrieval Service**: 
    - *Responsibility*: Exposes semantic and hybrid search capabilities over the vector store to the Agent Platform.

### Domain: Knowledge Acquisition (Ingestion Pipeline)
15. **Data Discovery Service**: 
    - *Responsibility*: Normalizes URLs and manages sitemaps/search-based discovery scheduling.
16. **Crawl Service**: 
    - *Responsibility*: Manages Crawl4AI workers, limits, rate policies, and stores raw HTML to S3.
17. **Document Processing Service**: 
    - *Responsibility*: Cleans boilerplate, converts content to Markdown, and extracts basic metadata.
18. **Knowledge Classification Service**: 
    - *Responsibility*: Determines relevance, tags topics, and identifies companies/roles for the processed documents.
19. **Deduplication Service**: 
    - *Responsibility*: Enforces exact hashing and near-duplicate semantic detection to preserve corpus quality.
20. **Embedding / Indexing Service**: 
    - *Responsibility*: Chunks text, calls embedding models, and loads data into MongoDB.

*Note: While logically independent to enforce boundaries, services 15-20 may be physically deployed as modules within a unified "Knowledge Ingestion Worker Service" processing Redis queues, provided they maintain data encapsulation.*
