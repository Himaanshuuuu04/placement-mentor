# Architecture Freeze Declaration

**Project:** AI-Powered Agentic Placement Mentor  
**Status:** ARCHITECTURE FROZEN  
**Date:** September 18, 2026

## Statement of Freeze

This document formally declares that the high-level architecture for the **AI-Powered Agentic Placement Mentor** has been finalized and frozen. The architecture aligns with the project synopsis and fulfills the requirements for a production-oriented, academic platform designed to prepare computer science students for placements through multi-agent orchestration, RAG, student knowledge tracing, and secure code execution.

All future implementation must adhere to this architectural source of truth. Any significant deviations, technology replacements, or structural changes must be formally proposed and documented as Architecture Decision Records (ADRs).

## Key Architectural Principles

1.  Modular microservices with clear bounded contexts and service ownership.
2.  API-driven synchronous communication and event-driven asynchronous workloads.
3.  Stateless services wherever practical, with explicit ownership of persistent state.
4.  Strict security boundaries for untrusted code execution (Firecracker microVMs + Judge0).
5.  Clear separation between authoritative business logic and probabilistic AI operations.
6.  Comprehensive observability and failure handling for all critical workflows.

## Documentation Index

The complete architectural specification is organized as follows:

### Architecture Domains
*   [System Context](architecture/01-system-context.md)
*   [Container Architecture](architecture/02-container-architecture.md)
*   [Service Boundaries](architecture/03-service-boundaries.md)
*   [Data Architecture](architecture/04-data-architecture.md)
*   [Event Architecture](architecture/05-event-architecture.md)
*   [API Architecture](architecture/06-api-architecture.md)
*   [RAG Architecture](architecture/07-rag-architecture.md)
*   [Ingestion Architecture](architecture/08-ingestion-architecture.md)
*   [Agent Architecture](architecture/09-agent-architecture.md)
*   [Execution Security](architecture/10-execution-security.md)
*   [Realtime Architecture](architecture/11-realtime-architecture.md)
*   [Security Architecture](architecture/12-security-architecture.md)
*   [Observability](architecture/13-observability.md)
*   [Deployment Architecture](architecture/14-deployment-architecture.md)
*   [Scalability](architecture/15-scalability.md)

### Database Schemas
*   [PostgreSQL Schema](database/postgres-schema.sql)
*   [MongoDB Schema](database/mongodb-schema.md)
*   [Indexes](database/indexes.md)
*   [Data Dictionary](database/data-dictionary.md)

### API & Events
*   [OpenAPI Specification](../api/openapi.yaml)
*   [Event Contracts](events/event-contracts.md)

### Diagrams
*   [System Context](diagrams/system-context.mmd)
*   [Containers](diagrams/containers.mmd)
*   [Ingestion](diagrams/ingestion.mmd)
*   [Agents](diagrams/agents.mmd)
*   [Execution](diagrams/execution.mmd)
*   [Realtime](diagrams/realtime.mmd)

### Architecture Decision Records (ADRs)
*   [ADR-001: Microservices architecture](adr/ADR-001.md)
*   [ADR-002: PostgreSQL as transactional source of truth](adr/ADR-002.md)
*   [ADR-003: MongoDB Vector Search for RAG](adr/ADR-003.md)
*   [ADR-004: Redis/BullMQ for asynchronous jobs](adr/ADR-004.md)
*   [ADR-005: S3 for raw document storage](adr/ADR-005.md)
*   [ADR-006: Crawl4AI for crawling](adr/ADR-006.md)
*   [ADR-007: LangGraph for agent orchestration](adr/ADR-007.md)
*   [ADR-008: Judge0 + Firecracker for execution](adr/ADR-008.md)
*   [ADR-009: WebSocket/WebRTC split](adr/ADR-009.md)
*   [ADR-010: Event-driven architecture](adr/ADR-010.md)
*   [ADR-011: Agent-to-service communication](adr/ADR-011.md)
*   [ADR-012: Document versioning and provenance](adr/ADR-012.md)
