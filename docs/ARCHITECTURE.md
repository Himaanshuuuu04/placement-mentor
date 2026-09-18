You are the Principal Software Architect and Staff Backend Engineer responsible for
freezing the architecture of a production-oriented academic project called:

"AI-Powered Agentic Placement Mentor"

You are not being asked to implement the system yet.

Your responsibility in this phase is to:
1. Analyze the project requirements.
2. Resolve architectural ambiguities.
3. Define service boundaries.
4. Define database schemas.
5. Define API contracts.
6. Define event contracts.
7. Define data ownership.
8. Define the RAG and ingestion architecture.
9. Define the AI-agent architecture.
10. Define deployment and infrastructure architecture.
11. Define security, observability, scalability and failure-handling strategies.
12. Produce documentation that can be treated as the architectural source of truth for all future implementation.

Do NOT start implementing application logic.
Do NOT generate large amounts of production code.
Do NOT arbitrarily introduce technologies.
Do NOT replace technologies already specified in the project without an explicit architectural justification.

==================================================
1. PROJECT CONTEXT
==================================================

The project is an AI-powered placement mentor for computer science students.

The system should support:

- personalized placement preparation
- company-specific preparation
- adaptive question generation
- student knowledge/mastery modelling
- coding assessment
- secure code execution
- AI-based code evaluation
- system design mentoring
- mock technical interviews
- persistent conversational state
- RAG over company/interview/technical knowledge
- personalized preparation roadmaps
- real-time text interaction
- real-time audio interaction
- multi-agent orchestration

The system should model a student's evolving knowledge state and adapt the preparation process accordingly.

The architecture must support both:

A. Student interaction workloads
B. Knowledge acquisition / web ingestion workloads

==================================================
2. SOURCE OF TRUTH
==================================================

Use the attached project synopsis as the primary project specification.

Important architecture already described in the synopsis:

- LangGraph for multi-agent orchestration.
- Large Language Models for reasoning, tutoring, generation, evaluation and interview simulation.
- LKT / CodeLKT / NTKT / IRT concepts for knowledge tracing and student modelling.
- PostgreSQL + PostgresSaver for persistent state and graph checkpoints.
- MongoDB Vector Search for company-specific RAG.
- Judge0 for code execution.
- Firecracker microVMs for isolated execution.
- WebSockets for realtime token/event communication.
- WebRTC for realtime interview audio.
- Next.js frontend.
- AWS S3 + CloudFront.
- AWS infrastructure including EC2/Lambda/VPC/security components.

Do not silently replace these technologies.

If you believe one of these technologies is unsuitable for a specific responsibility,
document the problem and propose an alternative as an ADR rather than silently changing
the architecture.

==================================================
3. ARCHITECTURAL PRINCIPLES
==================================================

The architecture must follow these principles:

1. Clear service ownership.
2. Loose coupling.
3. API-driven communication.
4. Event-driven communication for asynchronous workloads.
5. Independent scalability of high-load components.
6. Stateless services wherever practical.
7. Persistent state must have an explicit owner.
8. AI components must not directly access arbitrary databases.
9. Agents must interact with the platform through explicit tools/services.
10. RAG must preserve provenance.
11. Raw documents and processed knowledge must be versioned.
12. Untrusted code must never execute inside the application service.
13. AI outputs must be treated as probabilistic.
14. Deterministic business logic should remain outside the LLM whenever practical.
15. Every important asynchronous operation must be observable.
16. Every critical AI operation must be reproducible using model/prompt/version metadata.
17. Avoid distributed-system complexity that provides no meaningful benefit to this project.

==================================================
4. ARCHITECTURAL STYLE
==================================================

Use a modular microservices architecture with clear bounded contexts.

Do not create a microservice merely because a component exists.

For every proposed service answer:

- What business responsibility does it own?
- What data does it own?
- Which APIs does it expose?
- Which events does it publish?
- Which events does it consume?
- What dependencies does it have?
- Can it scale independently?
- Why should it be a separate service?
- What failure occurs if this service is unavailable?

The proposed logical domains should include at minimum:

1. API Gateway / BFF
2. Identity / User Service
3. Company & Role Service
4. Topic / Competency Service
5. Question Bank Service
6. Assessment Service
7. Code Execution Service
8. Evaluation Service
9. Knowledge Tracing / Mastery Service
10. Interview Service
11. Roadmap / Personalization Service
12. Agent Orchestrator
13. Retrieval Service
14. Data Discovery Service
15. Crawl Service
16. Document Processing Service
17. Knowledge Classification Service
18. Deduplication Service
19. Embedding / Indexing Service
20. Realtime Gateway

You may merge services if there is a strong reason.

You must document all merges.

==================================================
5. HIGH LEVEL ARCHITECTURE
==================================================

Design the architecture around the following major planes:

PLANE A — Student / Learning Platform

Responsible for:
- user
- profile
- target company
- target role
- questions
- assessments
- submissions
- evaluations
- mastery
- roadmaps
- interview history

PLANE B — AI / Agent Platform

Responsible for:
- LangGraph orchestration
- routing
- tool invocation
- interview conductor
- code evaluator agent
- system design mentor
- knowledge tracer
- question generation
- feedback generation
- persistent agent checkpoints

PLANE C — Knowledge Acquisition Platform

Responsible for:
- source configuration
- URL discovery
- sitemap discovery
- search-based discovery
- crawl scheduling
- Crawl4AI workers
- document extraction
- document normalization
- relevance detection
- classification
- deduplication
- chunking
- embeddings
- indexing

PLANE D — Secure Execution Platform

Responsible for:
- submission execution
- Judge0
- Firecracker
- resource limits
- execution lifecycle
- execution result collection

PLANE E — Realtime Platform

Responsible for:
- WebSocket connections
- streaming
- session presence
- realtime interview events
- WebRTC signaling
- audio-related event handling

==================================================
6. DATA OWNERSHIP
==================================================

Create a "Data Ownership Matrix".

For every entity specify:

Entity
Owning Service
Storage
Write Access
Read Access
Source of Truth
Caching Strategy
Retention Policy

Entities should include at minimum:

User
UserProfile
Company
Role
Competency
Topic
Question
QuestionTopic
Assessment
AssessmentQuestion
Submission
ExecutionJob
ExecutionResult
Evaluation
StudentMastery
MasteryEvent
InterviewSession
InterviewTurn
InterviewFeedback
Roadmap
RoadmapItem
KnowledgeSource
CrawlJob
DiscoveredURL
Document
DocumentVersion
DocumentChunk
Embedding
AgentSession
AgentCheckpoint

Important rule:

No service should directly modify another service's database tables.

Cross-service communication must happen through:
- API
- event
- explicitly documented shared infrastructure

Avoid cross-service foreign keys.

==================================================
7. DATABASE ARCHITECTURE
==================================================

Design three storage categories.

A. PostgreSQL

PostgreSQL is the system of record for transactional/application state.

Design normalized relational schemas for:

users
user_profiles
companies
roles
role_competencies
topics
questions
question_topics
question_companies
assessments
assessment_questions
submissions
execution_jobs
execution_results
evaluations
student_mastery
mastery_events
interview_sessions
interview_turns
interview_feedback
learning_roadmaps
roadmap_items
knowledge_sources
crawl_jobs
discovered_urls
documents
document_versions

For each table define:

- column
- type
- nullable
- default
- primary key
- foreign key where internally appropriate
- unique constraints
- indexes
- check constraints

Also provide:

- migration ordering
- indexing strategy
- expected high-cardinality columns
- expected query patterns
- partitioning candidates if needed
- retention/archive strategy

Do not introduce partitioning just for theoretical scalability.
Only propose it when justified by expected data growth.

==================================================
8. MONGODB KNOWLEDGE SCHEMA
==================================================

MongoDB should be used for the RAG knowledge layer.

Design schemas for:

knowledge_documents
knowledge_chunks

A document should preserve:

- document ID
- version
- canonical URL
- title
- source
- source type
- company
- role
- topics
- publication date
- crawl date
- content hash
- relevance information
- quality metadata
- storage URI
- provenance

A chunk should preserve:

- chunk ID
- document ID
- document version
- chunk index
- text
- section path
- embedding
- company IDs
- role IDs
- topic IDs
- source type
- document type
- language
- token count

Design MongoDB indexes for:

1. vector search
2. metadata filtering
3. full-text search
4. document lookup
5. deduplication

Explain the indexing strategy.

==================================================
9. RAW DOCUMENT STORAGE
==================================================

Use S3-compatible object storage for raw ingestion artifacts.

Define object conventions such as:

raw/
processed/
markdown/
documents/
crawl-runs/
versions/

Define the naming strategy.

Example:

s3://knowledge-bucket/raw/{document_id}/v{version}/page.html

Also define:

- retention
- versioning
- lifecycle policies
- access policy
- encryption
- metadata

==================================================
10. REDIS ARCHITECTURE
==================================================

Redis should NOT be the system of record.

Use Redis for:

- BullMQ queues
- short-lived cache
- rate limiting
- distributed locks
- realtime presence where appropriate
- temporary processing state

Define queues:

crawl-discovery
crawl-fetch
document-process
document-classify
document-deduplicate
document-chunk
document-embed
evaluation
mastery-update
question-generation

For every queue define:

- producer
- consumer
- message schema
- retry policy
- max attempts
- dead-letter strategy
- idempotency strategy
- concurrency
- ordering requirement

==================================================
11. EVENT ARCHITECTURE
==================================================

Design the event-driven communication model.

Events should include at minimum:

UserCreated
TargetRoleChanged

AssessmentStarted
SubmissionCreated

ExecutionRequested
ExecutionCompleted

EvaluationCompleted
MasteryUpdated

InterviewStarted
InterviewTurnCreated
InterviewCompleted

RoadmapGenerated
RoadmapUpdated

CrawlJobCreated
URLDiscovered
PageCrawled
DocumentProcessed
DocumentClassified
DocumentDeduplicated
EmbeddingCreated
KnowledgeIndexed

For every event define:

{
  event_id,
  event_type,
  schema_version,
  occurred_at,
  producer,
  correlation_id,
  causation_id,
  payload
}

Explain:

- delivery semantics
- retry behavior
- idempotency
- ordering assumptions
- duplicate handling
- poison-message handling
- schema versioning

==================================================
12. API CONTRACTS
==================================================

Define REST APIs for all externally meaningful services.

At minimum:

/users
/companies
/roles
/topics
/questions
/assessments
/submissions
/evaluations
/mastery
/interviews
/roadmaps
/retrieval
/ingestion

For every endpoint define:

HTTP method
URL
authentication
authorization
request
response
validation
error response
status codes
idempotency
rate limits

Use OpenAPI 3.1 style definitions.

Do not implement the APIs yet.

==================================================
13. RAG ARCHITECTURE
==================================================

Design the complete retrieval pipeline:

User Query
    ↓
Query normalization
    ↓
Intent/topic extraction
    ↓
Metadata filtering
    ↓
Vector retrieval
    +
Keyword retrieval
    ↓
Hybrid ranking
    ↓
Reranking
    ↓
Context assembly
    ↓
LLM

Define:

- embedding model abstraction
- vector dimensions as configurable
- chunking strategy
- overlap strategy
- metadata strategy
- retrieval top-k
- reranking
- filters
- citation/provenance
- context limits

The system must preserve document provenance all the way from:

source URL
→ document
→ version
→ chunk
→ retrieval result
→ generated answer

==================================================
14. WEB INGESTION ARCHITECTURE
==================================================

Crawl4AI is the crawler.

Do not treat Crawl4AI as the entire ingestion system.

Define separate components:

Discovery Service
Crawler Service
Document Processor
Relevance Classifier
Deduplication Service
Chunking Service
Embedding Service

The pipeline should be:

Source
 ↓
Discovery
 ↓
URL normalization
 ↓
URL queue
 ↓
Crawl4AI
 ↓
Raw HTML / Markdown
 ↓
Normalization
 ↓
Relevance classification
 ↓
Metadata extraction
 ↓
Deduplication
 ↓
Chunking
 ↓
Embedding
 ↓
MongoDB

Support:

- sitemap discovery
- search-based discovery
- scheduled recrawling
- robots.txt policy handling
- domain restrictions
- crawl rate limits
- retry
- backoff
- crawl depth
- relevance-based prioritization

Define how the crawler prevents:

- infinite crawling
- duplicate URLs
- duplicate content
- malicious redirects
- SSRF
- huge pages
- resource exhaustion
- unexpected file downloads

==================================================
15. DOCUMENT PROCESSING
==================================================

Define a normalization pipeline:

HTML
 ↓
Main-content extraction
 ↓
Boilerplate removal
 ↓
Markdown
 ↓
Metadata extraction
 ↓
Language detection
 ↓
Document type classification
 ↓
Topic classification
 ↓
Company extraction
 ↓
Role extraction
 ↓
Quality/relevance assessment
 ↓
Chunking

Define the metadata taxonomy.

At minimum:

source_type
document_type
company
role
topic
difficulty
language
published_at
author
confidence
relevance_score

Do not embed content that fails the configured relevance threshold.

==================================================
16. DEDUPLICATION
==================================================

Design three deduplication levels:

Level 1:
URL canonicalization

Level 2:
Exact content hashing

Level 3:
Near-duplicate semantic detection

Explain:

- normalization
- hashing
- similarity threshold
- versioning
- source preservation
- duplicate handling

Do not destroy provenance.

If two sites contain the same information, preserve the source relationship.

==================================================
17. KNOWLEDGE TRACING ARCHITECTURE
==================================================

The student mastery model must be multidimensional.

At minimum model:

- correctness
- algorithmic understanding
- time complexity
- space complexity
- reasoning
- code quality
- conceptual understanding
- confidence

Define:

student_mastery
mastery_events

The current mastery state should be derived from events and updates.

Design the update workflow:

Submission
 ↓
Execution
 ↓
Evaluation
 ↓
Knowledge signals
 ↓
Mastery update
 ↓
MasteryUpdated event
 ↓
Roadmap / Question Generator

Keep raw observations separate from derived mastery state.

==================================================
18. LANGGRAPH ARCHITECTURE
==================================================

Define the LangGraph state.

The graph should include concepts such as:

Router
Code Evaluator
Interview Conductor
System Design Mentor
Knowledge Tracer
Question Generator
Feedback Generator

For each node specify:

- responsibility
- inputs
- outputs
- tools
- failure behavior
- persistence requirements
- token/context requirements

Agents must not directly modify databases.

Agents call service APIs/tools.

Example:

Agent
 ↓
Mastery API
 ↓
Mastery Service
 ↓
PostgreSQL

not:

Agent
 ↓
PostgreSQL directly

==================================================
19. AGENT STATE
==================================================

Define a shared graph state containing only what is required.

Example categories:

session
user
target
mastery
conversation
retrieval_context
current_question
evaluation
next_action

Separate:

Short-term conversational state
Long-term user state
Persistent mastery state
Agent checkpoint state

Do not duplicate authoritative business data inside agent state.

==================================================
20. SECURE CODE EXECUTION
==================================================

Design:

Frontend
 ↓
Assessment Service
 ↓
Code Execution Service
 ↓
Judge0
 ↓
Firecracker
 ↓
Execution Result
 ↓
Evaluation Service

Define isolation boundaries.

Define:

CPU limits
Memory limits
Time limits
Process limits
Filesystem limits
Network policy
Container/microVM lifecycle
Timeouts
Cleanup
Logging

Assume submitted code is malicious.

Threats must include:

fork bombs
infinite loops
memory exhaustion
filesystem escape
network abuse
privilege escalation
malicious binaries
resource exhaustion

==================================================
21. INTERVIEW ARCHITECTURE
==================================================

Design:

Text Interview:

Client
 ↓
WebSocket Gateway
 ↓
Interview Service
 ↓
LangGraph
 ↓
Retrieval / Mastery / Question services
 ↓
Response stream

Audio Interview:

Client
 ↓
WebRTC
 ↓
Media / Signaling layer
 ↓
Speech pipeline
 ↓
Interview Service
 ↓
LangGraph

Define clearly what WebSocket does and what WebRTC does.

Do not use WebRTC merely because audio exists.

==================================================
22. ROADMAP / PERSONALIZATION
==================================================

Design the personalization system.

Inputs:

student mastery
target company
target role
preparation timeline
previous mistakes
question history
interview performance

Outputs:

learning roadmap
topics
priority
difficulty
practice schedule
revision schedule

Do not make the roadmap generator a free-form LLM only.

Use deterministic constraints and scoring around the LLM.

==================================================
23. SECURITY ARCHITECTURE
==================================================

Create a threat model.

At minimum analyze:

Authentication
Authorization
RBAC
API abuse
Rate limiting
Prompt injection
Indirect prompt injection through webpages
SSRF
Malicious webpages
Data poisoning
RAG poisoning
Data leakage
Tenant isolation
Secrets management
Code execution escape
WebSocket abuse
WebRTC abuse
S3 access
Database exposure
Internal service authentication

Clearly distinguish:

Trusted data
Untrusted user input
Untrusted web content
LLM-generated output
Executable code

Never treat scraped webpages as trusted instructions.

==================================================
24. OBSERVABILITY
==================================================

Define:

Structured logging
Metrics
Distributed tracing
Correlation IDs
Request IDs
Event IDs

Metrics should include:

API latency
p50
p95
p99

crawl success rate
crawl failure rate
queue depth
queue processing latency

RAG retrieval latency
RAG hit rate
retrieval precision

LLM latency
LLM token usage
LLM failure rate

code execution latency
execution failure rate

WebSocket connection count

agent node latency

mastery update latency

Define what should be logged and what must NEVER be logged.

==================================================
25. FAILURE HANDLING
==================================================

For every major service define:

- timeout
- retry
- exponential backoff
- circuit breaker where applicable
- dead-letter queue
- idempotency
- fallback
- degraded mode

Examples:

MongoDB unavailable
LLM unavailable
Crawl4AI unavailable
Redis unavailable
Judge0 unavailable
S3 unavailable
PostgreSQL unavailable

The architecture must define what the user experiences in each situation.

==================================================
26. SCALABILITY
==================================================

Identify independently scalable components.

Expected scaling candidates include:

Crawl workers
Embedding workers
Evaluation workers
Code execution workers
Realtime gateway
API gateway
LangGraph workers

Explain:

vertical scaling
horizontal scaling
queue-based scaling
worker concurrency

Do not claim "infinite scalability".

Give realistic bottlenecks.

==================================================
27. DEPLOYMENT ARCHITECTURE
==================================================

Design local and AWS environments.

LOCAL:

Docker Compose should run:

PostgreSQL
MongoDB or MongoDB Atlas
Redis
MinIO
Crawl4AI
backend services

AWS:

EC2 / ECS / Lambda / S3 / CloudFront / VPC as justified.

Do not force every service onto a separate EC2 instance.

For every infrastructure component explain why it exists.

==================================================
28. NETWORK ARCHITECTURE
==================================================

Define:

Internet-facing components
Private services
Database subnet
Worker subnet
Code-execution isolation boundary
Internal service communication
TLS termination
VPC boundaries
Security groups
Outbound restrictions

Clearly identify what is publicly accessible.

==================================================
29. C4 MODEL
==================================================

Generate:

C4 Level 1:
System Context

C4 Level 2:
Container Diagram

C4 Level 3:
Component diagrams for:

Agent Platform
Knowledge Ingestion Platform
Assessment/Execution Platform

Use Mermaid or PlantUML.

==================================================
30. SEQUENCE DIAGRAMS
==================================================

Create sequence diagrams for:

1. User registration
2. Target company selection
3. Adaptive question generation
4. Code submission
5. Code execution
6. Code evaluation
7. Mastery update
8. RAG query
9. Knowledge ingestion
10. Crawl retry
11. Mock interview
12. Interview completion
13. Roadmap generation

==================================================
31. ARCHITECTURE DECISION RECORDS
==================================================

Create ADRs for at least:

ADR-001 Microservices architecture
ADR-002 PostgreSQL as transactional source of truth
ADR-003 MongoDB Vector Search for RAG
ADR-004 Redis/BullMQ for asynchronous jobs
ADR-005 S3 for raw document storage
ADR-006 Crawl4AI for crawling
ADR-007 LangGraph for agent orchestration
ADR-008 Judge0 + Firecracker for execution
ADR-009 WebSocket/WebRTC split
ADR-010 Event-driven architecture
ADR-011 Agent-to-service communication
ADR-012 Document versioning and provenance

Each ADR must contain:

Context
Decision
Alternatives
Advantages
Disadvantages
Consequences
Status

==================================================
32. API + EVENT VERSIONING
==================================================

Define versioning strategy.

REST:
 /api/v1/...

Events:
schema_version

Never make breaking changes without versioning.

==================================================
33. TESTING STRATEGY
==================================================

Define:

unit tests
integration tests
contract tests
end-to-end tests
load tests
security tests
LLM evaluation tests
RAG evaluation tests
sandbox security tests

Every service must have defined test boundaries.

==================================================
34. COST ARCHITECTURE
==================================================

Estimate the major cost drivers qualitatively.

Identify:

LLM inference
embeddings
AWS compute
database
storage
network
crawl volume
code execution

Explain where batching, caching and asynchronous processing reduce cost.

==================================================
35. DESIGN CONSTRAINT
==================================================

This is a college major project.

The architecture must be:

- technically sophisticated
- academically defensible
- implementable by a small student team
- explainable during project viva
- deployable with reasonable resources

Avoid unnecessary enterprise complexity.

Prefer:

simple distributed architecture
over
distributed architecture for appearance.

==================================================
36. REQUIRED DOCUMENTATION OUTPUT
==================================================

Create this documentation structure:

docs/
├── architecture/
│   ├── 01-system-context.md
│   ├── 02-container-architecture.md
│   ├── 03-service-boundaries.md
│   ├── 04-data-architecture.md
│   ├── 05-event-architecture.md
│   ├── 06-api-architecture.md
│   ├── 07-rag-architecture.md
│   ├── 08-ingestion-architecture.md
│   ├── 09-agent-architecture.md
│   ├── 10-execution-security.md
│   ├── 11-realtime-architecture.md
│   ├── 12-security-architecture.md
│   ├── 13-observability.md
│   ├── 14-deployment-architecture.md
│   └── 15-scalability.md
│
├── database/
│   ├── postgres-schema.sql
│   ├── mongodb-schema.md
│   ├── indexes.md
│   └── data-dictionary.md
│
├── api/
│   └── openapi.yaml
│
├── events/
│   └── event-contracts.md
│
├── diagrams/
│   ├── system-context.mmd
│   ├── containers.mmd
│   ├── ingestion.mmd
│   ├── agents.mmd
│   ├── execution.mmd
│   └── realtime.mmd
│
└── adr/
    ├── ADR-001.md
    ├── ADR-002.md
    ...