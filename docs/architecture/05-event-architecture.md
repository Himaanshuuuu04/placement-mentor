# 05. Event Architecture

## 1. Overview
The system employs an Event-Driven Architecture (EDA) to decouple heavy, asynchronous workloads from the synchronous user request path. Communication is mediated by Redis and BullMQ, facilitating reliable message passing between distinct bounded contexts.

## 2. Event Schema Standard
All events adhere to a universal JSON schema to guarantee traceability, allow for safe evolution, and support idempotency.

```json
{
  "event_id": "uuid-v4",
  "event_type": "MasteryUpdated",
  "schema_version": "1.0",
  "occurred_at": "2026-09-18T12:00:00Z",
  "producer": "mastery-service",
  "correlation_id": "req-uuid-from-api-gateway",
  "causation_id": "eval-uuid-that-caused-this",
  "payload": {
    "student_id": "uuid-v4",
    "topic_id": "uuid-v4",
    "new_score": 0.85,
    "confidence": 0.92
  }
}
```

## 3. Core Event Catalog

### Learning & Assessment Domain
- `UserCreated`: Emitted by Identity Service. Triggers generation of a default profile and roadmap.
- `TargetRoleChanged`: Emitted by Company/Role Service. Triggers roadmap recalculation.
- `AssessmentStarted`: Emitted by Assessment Service.
- `SubmissionCreated`: Emitted by Assessment Service. Triggers execution.
- `ExecutionRequested`: Emitted to Code Execution Service.
- `ExecutionCompleted`: Emitted by Code Execution Service. Consumed by Evaluation Service.
- `EvaluationCompleted`: Emitted by Evaluation Service. Consumed by Mastery Service to update LKT models.
- `MasteryUpdated`: Emitted by Mastery Service. Consumed by Roadmap / Question Generator Services to adapt future content.

### Interview & Agent Domain
- `InterviewStarted`: Emitted when an interview session opens.
- `InterviewTurnCreated`: Emitted per interaction turn.
- `InterviewCompleted`: Emitted at session end. Triggers comprehensive feedback generation.
- `RoadmapGenerated` / `RoadmapUpdated`: Signals changes to a student's study plan.

### Knowledge Acquisition Domain (Ingestion Pipeline)
- `CrawlJobCreated`: Initiates a new ingestion run.
- `URLDiscovered`: Emitted by Discovery Service.
- `PageCrawled`: Emitted by Crawl Service once raw HTML is stored in S3.
- `DocumentProcessed`: Boilerplate removed and converted to Markdown.
- `DocumentClassified`: Relevance and topics attached.
- `DocumentDeduplicated`: Passed similarity/hash checks.
- `EmbeddingCreated` / `KnowledgeIndexed`: Content is officially available in MongoDB for RAG.

## 4. Delivery Semantics & Reliability

- **Delivery Semantics**: The system guarantees *At-Least-Once* delivery using Redis/BullMQ. If a worker crashes mid-process, the job returns to the queue.
- **Idempotency**: Consumers MUST be designed to handle duplicate events. Deduplication is handled via the `event_id` and database mechanisms (e.g., `UPSERT` / `ON CONFLICT` constraints).
- **Retry & Backoff**: Configured with exponential backoff for ephemeral failures (e.g., external API rate limits, temporary DB locks).
- **Poison-Message Handling**: Messages failing beyond maximum retry attempts are routed to a Dead-Letter Queue (DLQ) for alerting and manual replay.
- **Ordering Assumptions**: Strict ordering is generally not guaranteed. In domains where sequence matters (e.g., `InterviewTurnCreated`), state machines, optimistic concurrency control, or version/sequence numbers in the database are used to resolve race conditions.
