# Event Architecture Contracts

This document defines the event-driven communication model for asynchronous workloads in the AI-Powered Agentic Placement Mentor.

## 1. Event Envelope Schema

All events must adhere to the following standard envelope (JSON format).

```json
{
  "event_id": "uuid",
  "event_type": "string",
  "schema_version": "string",
  "occurred_at": "iso8601 timestamp",
  "producer": "string (service name)",
  "correlation_id": "uuid (optional, traces flow)",
  "causation_id": "uuid (optional, id of event causing this)",
  "payload": {
    // Specific event data
  }
}
```

## 2. Event Delivery & Semantics

- **Delivery Semantics:** At-least-once delivery guaranteed through Redis BullMQ streams/queues. Consumers must ensure idempotency.
- **Retry Behavior:** Configurable exponential backoff (e.g., 3 retries max for regular events, 5 for critical events).
- **Idempotency:** Consumers track `event_id` or logical state mutations (e.g. updating mastery if timestamp > current).
- **Ordering Assumptions:** strict causal ordering is generally not guaranteed except where partitioned by entity ID (e.g., `user_id` routing to ensure chronological processing for a specific user).
- **Duplicate Handling:** Deduplicated via cache (Redis) based on `event_id` and idempotency constraints in the database.
- **Poison-Message Handling:** Messages failing after max retries are moved to a Dead-Letter Queue (DLQ) for manual inspection and alerts.
- **Schema Versioning:** `schema_version` is utilized. Breaking changes to events should introduce a new `event_type` (e.g., `SubmissionCreated.v2`) or new `schema_version` gracefully handled by backward-compatible consumers.

---

## 3. Core Domain Events

### User & Profile Events
- **UserCreated**
  - *Producer:* Identity/User Service
  - *Payload:* `userId`, `email`, `createdAt`
- **TargetRoleChanged**
  - *Producer:* Profile Service
  - *Payload:* `userId`, `oldRoleId`, `newRoleId`, `companyId`

### Assessment & Execution Events
- **AssessmentStarted**
  - *Producer:* Assessment Service
  - *Payload:* `assessmentId`, `userId`, `type`
- **SubmissionCreated**
  - *Producer:* Assessment Service
  - *Payload:* `submissionId`, `assessmentId`, `questionId`, `userId`, `language`
- **ExecutionRequested**
  - *Producer:* Assessment Service
  - *Payload:* `executionId`, `submissionId`, `code`, `language`, `tests`
- **ExecutionCompleted**
  - *Producer:* Code Execution Service (Judge0/Firecracker)
  - *Payload:* `executionId`, `status`, `time`, `memory`, `testResults`

### Evaluation & Mastery Events
- **EvaluationCompleted**
  - *Producer:* Evaluation Service (AI)
  - *Payload:* `evaluationId`, `submissionId`, `metrics` (correctness, time complexity, etc.)
- **MasteryUpdated**
  - *Producer:* Knowledge Tracing/Mastery Service
  - *Payload:* `userId`, `topicId`, `newScore`, `confidenceDelta`

### Interview Events
- **InterviewStarted**
  - *Producer:* Interview Service
  - *Payload:* `interviewId`, `userId`, `type` (text/audio)
- **InterviewTurnCreated**
  - *Producer:* Interview Service
  - *Payload:* `interviewId`, `turnId`, `speaker`, `text`
- **InterviewCompleted**
  - *Producer:* Interview Service
  - *Payload:* `interviewId`, `duration`, `summaryId`

### Personalization Events
- **RoadmapGenerated**
  - *Producer:* Roadmap/Personalization Service
  - *Payload:* `roadmapId`, `userId`, `topics`
- **RoadmapUpdated**
  - *Producer:* Roadmap/Personalization Service
  - *Payload:* `roadmapId`, `userId`, `progressUpdates`

---

## 4. Knowledge Ingestion Events

- **CrawlJobCreated**
  - *Producer:* Crawl Service
  - *Payload:* `jobId`, `seedUrl`, `configuration`
- **URLDiscovered**
  - *Producer:* Discovery Service
  - *Payload:* `url`, `sourceJobId`, `depth`
- **PageCrawled**
  - *Producer:* Crawl4AI Workers
  - *Payload:* `url`, `rawStoragePath`, `statusCode`
- **DocumentProcessed**
  - *Producer:* Document Processing Service
  - *Payload:* `documentId`, `markdownPath`, `language`
- **DocumentClassified**
  - *Producer:* Knowledge Classification Service
  - *Payload:* `documentId`, `sourceType`, `documentType`, `companyId`, `roleId`, `topicIds`
- **DocumentDeduplicated**
  - *Producer:* Deduplication Service
  - *Payload:* `documentId`, `status` (canonical/duplicate), `canonicalDocumentId`
- **EmbeddingCreated**
  - *Producer:* Embedding Service
  - *Payload:* `chunkId`, `documentId`, `embeddingModel`, `dimensions`
- **KnowledgeIndexed**
  - *Producer:* Indexing Service
  - *Payload:* `documentId`, `indexedChunkCount`, `vectorStore` (MongoDB Vector)
