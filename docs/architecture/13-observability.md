# Observability Architecture

## 1. Overview
The Observability architecture ensures that the system's distributed components, AI interactions, and asynchronous workflows are fully transparent. It relies on structured logging, metrics, and distributed tracing.

## 2. Distributed Tracing and Correlation
Every request entering the system is assigned a `Request ID` and `Correlation ID`.
- **Correlation ID:** Passed across all microservices, API boundaries, and asynchronous message queues to track the full lifecycle of a workflow.
- **Event ID & Causation ID:** Events published to the message broker include the `Event ID` (unique identifier) and `Causation ID` (the ID of the event that triggered this action) to trace event-driven chains.

## 3. Structured Logging
Logs must be structured as JSON.
- **Must Log:** API boundaries, asynchronous job starts/failures, Agent routing decisions, LLM invocation metadata (prompt template version, model version), and authentication events.
- **Must NEVER Log:** User passwords, raw PII (Personally Identifiable Information), secure tokens/keys, and raw sensitive user code submissions (except in secure audit logs if strictly required).

## 4. Key Metrics

### 4.1 API & Service Metrics
- **API Latency:** Tracked at p50, p95, and p99 percentiles.
- **Error Rates:** HTTP 4xx and 5xx error rates per endpoint.

### 4.2 Ingestion & Processing Metrics
- **Crawl Success/Failure Rate:** Ratio of successful page fetches vs timeouts/errors.
- **Queue Depth & Latency:** Monitoring Redis/BullMQ queue depths (e.g., `document-process`) and time-in-queue.

### 4.3 AI & RAG Metrics
- **RAG Retrieval Latency:** Time taken to query MongoDB Vector Search and rerank.
- **RAG Hit Rate & Precision:** Measuring the effectiveness and relevance of retrieved chunks.
- **LLM Latency & Token Usage:** Tracking inference time and token consumption for cost analysis.
- **LLM Failure Rate:** Rate of timeouts or malformed outputs from the LLM provider.
- **Agent Node Latency:** Time spent within individual LangGraph nodes.

### 4.4 Execution & Realtime Metrics
- **Code Execution Latency:** Time taken by Judge0 and Firecracker to return results.
- **Execution Failure Rate:** Rate of timeouts or infrastructure failures in the execution sandbox.
- **WebSocket Connection Count:** Active real-time connections per gateway instance.
- **Mastery Update Latency:** Time required to process `MasteryUpdated` events.
